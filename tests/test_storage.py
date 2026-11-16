import pandas as pd

from src.processing.storage import BiomarkerStore


def registro(archivo, grupo, longitud):
    return {
        "archivo": archivo, "grupo": grupo, "puntos_totales": 100, "secciones": 10,
        "longitud_total_um": longitud, "bifurcaciones": 4, "terminales": 5,
        "strahler_max": 2, "ratio_bifurcacion_terminal": 0.8,
    }


def test_guardar_y_leer_dashboard(tmp_path):
    store = BiomarkerStore(tmp_path / "test.sqlite3")
    store.save_biomarkers([registro("viejo.swc", "sana", 1.0)])
    # Mismo camino que main.py: DataFrame -> to_dict("records")
    df = pd.DataFrame([registro("a.swc", "sana", 100.0), registro("b.swc", "alzheimer", 50.0)])
    run_id = store.save_biomarkers(df.to_dict("records"), source="test")

    todo = store.dashboard()
    assert todo["run"]["id"] == run_id
    assert [r["archivo"] for r in todo["records"]] == ["b.swc", "a.swc"]  # solo la ultima ejecucion
    assert todo["summaries"]["sana"]["mean_length"] == 100.0

    sanas = store.dashboard("sana")
    assert [r["archivo"] for r in sanas["records"]] == ["a.swc"]
    assert set(sanas["summaries"]) == {"sana"}
