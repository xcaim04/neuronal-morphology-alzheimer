from streamlit.testing.v1 import AppTest

import predecir
from src.processing.storage import BiomarkerStore
from tests.test_prediccion import escribir_informe


def registro(archivo, grupo, longitud):
    return {
        "archivo": archivo, "grupo": grupo, "puntos_totales": 100, "secciones": 10,
        "longitud_total_um": longitud, "bifurcaciones": 4, "terminales": 5,
        "strahler_max": 2, "ratio_bifurcacion_terminal": 0.8,
    }


def arrancar(monkeypatch, ruta):
    # La app usa BiomarkerStore() sin argumentos: redirigimos el valor por defecto.
    monkeypatch.setattr(BiomarkerStore.__init__, "__defaults__", (ruta,))
    # Aislar el aviso del modelo del informe real de resultados/.
    monkeypatch.setattr(predecir, "RESULTADOS_EVALUACION", str(ruta.parent))
    return AppTest.from_file("../app.py", default_timeout=30).run()


def test_bd_vacia_muestra_aviso(monkeypatch, tmp_path):
    app = arrancar(monkeypatch, tmp_path / "vacia.sqlite3")
    assert not app.exception
    assert "main.py" in app.warning[0].value
    assert not app.metric


def test_bd_poblada_muestra_tarjetas(monkeypatch, tmp_path):
    ruta = tmp_path / "llena.sqlite3"
    store = BiomarkerStore(ruta)
    store.save_biomarkers([registro("a.swc", "sana", 100.0), registro("b.swc", "alzheimer", 50.0)])
    metrica = {"mean": 0.7, "std": 0.1}
    base = {"mean": 0.5, "std": 0.0}
    nombres = ["accuracy", "precision", "recall", "f1", "auc"]
    store.save_training_run(
        model_name="RandomForest", sample_count=2, healthy_count=1, alzheimer_count=1,
        metrics={"cv": dict.fromkeys(nombres, metrica), "linea_base": dict.fromkeys(nombres, base)},
        features=["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"],
    )

    escribir_informe(tmp_path, 0.501, 0.151)

    app = arrancar(monkeypatch, ruta)
    assert not app.exception
    assert [w.value for w in app.warning] == [predecir.aviso_azar()]
    etiquetas = [m.label for m in app.metric]
    assert etiquetas.count("Neuronas") == 2
    assert "accuracy (± 0.100)" in etiquetas
