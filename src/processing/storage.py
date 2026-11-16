import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DATABASE = Path(__file__).resolve().parents[2] / "data" / "neurona.sqlite3"


class BiomarkerStore:
    """Persiste biomarcadores y ejecuciones de entrenamiento en SQLite."""

    def __init__(self, database_path: str | Path = DEFAULT_DATABASE):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS biomarker_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'dataset'
                );

                CREATE TABLE IF NOT EXISTS biomarkers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL REFERENCES biomarker_runs(id) ON DELETE CASCADE,
                    archivo TEXT NOT NULL,
                    grupo TEXT NOT NULL CHECK (grupo IN ('sana', 'alzheimer')),
                    puntos_totales INTEGER NOT NULL,
                    secciones INTEGER NOT NULL,
                    longitud_total_um REAL NOT NULL,
                    bifurcaciones INTEGER NOT NULL,
                    terminales INTEGER NOT NULL,
                    strahler_max INTEGER NOT NULL,
                    ratio_bifurcacion_terminal REAL NOT NULL,
                    UNIQUE(run_id, archivo)
                );

                CREATE TABLE IF NOT EXISTS training_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    sample_count INTEGER NOT NULL,
                    healthy_count INTEGER NOT NULL,
                    alzheimer_count INTEGER NOT NULL,
                    metrics_json TEXT NOT NULL,
                    features_json TEXT NOT NULL
                );
                """
            )

    def save_biomarkers(self, records: list[dict[str, Any]], source: str = "dataset") -> int:
        if not records:
            raise ValueError("No hay biomarcadores para guardar")

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO biomarker_runs (created_at, source) VALUES (?, ?)",
                (created_at, source),
            )
            run_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO biomarkers (
                    run_id, archivo, grupo, puntos_totales, secciones,
                    longitud_total_um, bifurcaciones, terminales, strahler_max,
                    ratio_bifurcacion_terminal
                ) VALUES (
                    :run_id, :archivo, :grupo, :puntos_totales, :secciones,
                    :longitud_total_um, :bifurcaciones, :terminales, :strahler_max,
                    :ratio_bifurcacion_terminal
                )
                """,
                ({**record, "run_id": run_id} for record in records),
            )
        return run_id

    def save_training_run(
        self,
        model_name: str,
        sample_count: int,
        healthy_count: int,
        alzheimer_count: int,
        metrics: dict[str, Any],
        features: list[str],
    ) -> int:
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO training_runs (
                    created_at, model_name, sample_count, healthy_count,
                    alzheimer_count, metrics_json, features_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    model_name,
                    sample_count,
                    healthy_count,
                    alzheimer_count,
                    json.dumps(metrics, allow_nan=False),
                    json.dumps(features),
                ),
            )
        return int(cursor.lastrowid)

    def dashboard(self, group: str | None = None) -> dict[str, Any]:
        # Un grupo desconocido no filtra, como antes
        group = group if group in {"sana", "alzheimer"} else None
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT b.id, b.run_id, b.archivo, b.grupo, b.puntos_totales,
                       b.secciones, b.longitud_total_um, b.bifurcaciones,
                       b.terminales, b.strahler_max, b.ratio_bifurcacion_terminal
                FROM biomarkers AS b
                WHERE b.run_id = (SELECT MAX(id) FROM biomarker_runs)
                  AND (:group IS NULL OR b.grupo = :group)
                ORDER BY b.grupo, b.archivo
                """,
                {"group": group},
            ).fetchall()
            latest_run = connection.execute(
                "SELECT id, created_at, source FROM biomarker_runs ORDER BY id DESC LIMIT 1"
            ).fetchone()
            trainings = connection.execute(
                """
                SELECT id, created_at, model_name, sample_count, healthy_count,
                       alzheimer_count, metrics_json, features_json
                FROM training_runs ORDER BY id DESC LIMIT 10
                """
            ).fetchall()

        records = [dict(row) for row in rows]
        summaries = {}
        for label in ("sana", "alzheimer"):
            items = [row for row in records if row["grupo"] == label]
            if items:
                summaries[label] = {
                    "count": len(items),
                    "mean_length": round(sum(item["longitud_total_um"] for item in items) / len(items), 2),
                    "mean_branches": round(sum(item["bifurcaciones"] for item in items) / len(items), 2),
                    "mean_terminals": round(sum(item["terminales"] for item in items) / len(items), 2),
                    "mean_strahler": round(sum(item["strahler_max"] for item in items) / len(items), 2),
                }

        return {
            "run": dict(latest_run) if latest_run else None,
            "records": records,
            "summaries": summaries,
            "training_runs": [
                {
                    **dict(row),
                    "metrics": json.loads(row["metrics_json"]),
                    "features": json.loads(row["features_json"]),
                }
                for row in trainings
            ],
        }