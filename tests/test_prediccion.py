import json

import numpy as np
import pandas as pd
import pytest

import predecir
from predecir import predecir_desde_csv
from src.classification.classifier import NeuronaClassifier


@pytest.fixture
def modelo_path(tmp_path):
    rng = np.random.default_rng(0)
    clasificador = NeuronaClassifier()
    sanas = pd.DataFrame(rng.normal([3500, 50, 55, 3], [200, 5, 5, 0.3], (10, 4)), columns=clasificador.features)
    enfermas = pd.DataFrame(rng.normal([2000, 10, 15, 2], [200, 5, 5, 0.3], (10, 4)), columns=clasificador.features)
    X, y, _ = clasificador.preparar_datos(sanas, enfermas)
    clasificador.entrenar(X, y)
    ruta = tmp_path / "modelo.pkl"
    clasificador.guardar(str(ruta))
    return str(ruta)


def test_predecir_desde_csv(tmp_path, modelo_path):
    entrada = tmp_path / "entrada.csv"
    salida = tmp_path / "salida.csv"
    pd.DataFrame({
        "longitud_total_um": [3500, 2000],
        "bifurcaciones": [50, 10],
        "terminales": [55, 15],
        "strahler_max": [3, 2],
    }).to_csv(entrada, index=False)

    df = predecir_desde_csv(str(entrada), str(salida), modelo_path=modelo_path)

    assert list(df["prediccion"]) == ["Sana", "Alzheimer"]
    np.testing.assert_allclose(df["probabilidad_sana"] + df["probabilidad_alzheimer"], 1)
    assert (df["confianza_porcentaje"] >= 50).all()
    assert list(pd.read_csv(salida).columns[-4:]) == [
        "prediccion", "probabilidad_sana", "probabilidad_alzheimer", "confianza_porcentaje"
    ]


def test_predecir_desde_csv_columna_faltante(tmp_path, modelo_path):
    entrada = tmp_path / "entrada.csv"
    pd.DataFrame({"longitud_total_um": [3500], "bifurcaciones": [50], "terminales": [55]}).to_csv(entrada, index=False)

    with pytest.raises(ValueError, match="strahler_max"):
        predecir_desde_csv(str(entrada), modelo_path=modelo_path)


def escribir_informe(carpeta, auc_mean, auc_std):
    informe = {"resultados": {"RandomForest": {
        "auc": {"mean": auc_mean, "std": auc_std}, "accuracy": {"mean": 0.498, "std": 0.130},
    }}}
    (carpeta / "informe_evaluacion.json").write_text(json.dumps(informe), encoding="utf-8")


def test_aviso_azar(tmp_path, monkeypatch):
    monkeypatch.setattr(predecir, "RESULTADOS_EVALUACION", str(tmp_path))
    assert predecir.aviso_azar() is None

    escribir_informe(tmp_path, 0.501, 0.151)
    aviso = predecir.aviso_azar()
    assert "AUC 0.50 ± 0.15" in aviso and "accuracy 0.50 ± 0.13" in aviso

    escribir_informe(tmp_path, 0.9, 0.05)
    assert predecir.aviso_azar() is None
