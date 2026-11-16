from types import SimpleNamespace

import pytest

from src.models.neuron import Neurona
from src.processing.analyzer import BiomarkerAnalyzer
from src.utils.geometry import calcular_distancia_euclidiana, calcular_longitud_seccion

SOMA = "1 1 0 0 0 5 -1"
# Raiz simple (Strahler 1): una sola seccion terminal.
RAIZ_SIMPLE = """
2 3 10 0 0 1 1
3 3 20 0 0 1 2
"""
# Raiz compleja (Strahler 3): arbol binario completo de 3 niveles -> 7 secciones, 3 bifurcaciones, 4 terminales.
RAIZ_COMPLEJA = """
4 3 0 10 0 1 1
5 3 0 20 0 1 4
6 3 5 25 0 1 5
7 3 -5 25 0 1 5
8 3 8 30 0 1 6
9 3 2 30 0 1 6
10 3 -2 30 0 1 7
11 3 -8 30 0 1 7
"""
# Axon que bifurca dos veces; no debe contar.
AXON = """
12 2 0 -10 0 1 1
13 2 0 -20 0 1 12
14 2 5 -25 0 1 13
15 2 -5 -25 0 1 13
16 2 8 -30 0 1 14
17 2 2 -30 0 1 14
18 2 -2 -30 0 1 15
19 2 -8 -30 0 1 15
"""


def escribir_swc(ruta, *bloques):
    ruta.write_text("\n".join([SOMA, *bloques]) + "\n")
    return str(ruta)


def test_distancia_y_longitud_seccion():
    assert calcular_distancia_euclidiana((0, 0, 0), (3, 4, 0)) == 5
    seccion = SimpleNamespace(points=[(0, 0, 0), (3, 4, 0), (3, 4, 12)])
    assert calcular_longitud_seccion(seccion) == 17
    assert calcular_longitud_seccion(SimpleNamespace(points=[(1, 1, 1)])) == 0


def test_strahler_usa_todas_las_raices(tmp_path):
    # Regresion: antes solo se miraba la primera raiz (la simple) y daba 1.
    neurona = Neurona(escribir_swc(tmp_path / "n.swc", RAIZ_SIMPLE, RAIZ_COMPLEJA), "sana")
    assert neurona.morphology.root_sections[0].children == []
    assert neurona.calcular_strahler() == 3


def test_bifurcaciones_terminales_y_longitud(tmp_path):
    bio = Neurona(escribir_swc(tmp_path / "n.swc", RAIZ_SIMPLE, RAIZ_COMPLEJA), "sana").extraer_biomarcadores()
    assert bio["secciones"] == 8
    assert bio["bifurcaciones"] == 3
    assert bio["terminales"] == 5
    assert bio["strahler_max"] == 3
    assert bio["ratio_bifurcacion_terminal"] == 0.6
    # morphio no incluye el tramo soma -> primer punto de cada raiz: 10 (raiz simple) + 10 (tronco) + ramas
    assert bio["longitud_total_um"] == pytest.approx(10 + 10 + 2 * 50**0.5 + 4 * 34**0.5, abs=0.01)


def test_axon_no_cuenta(tmp_path):
    sin_axon = Neurona(escribir_swc(tmp_path / "a.swc", RAIZ_SIMPLE), "sana").extraer_biomarcadores()
    # El axon va primero y es mas complejo que la dendrita.
    con_axon = Neurona(escribir_swc(tmp_path / "b.swc", AXON, RAIZ_SIMPLE), "sana").extraer_biomarcadores()
    claves = ["puntos_totales", "secciones", "longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]
    assert {k: con_axon[k] for k in claves} == {k: sin_axon[k] for k in claves}
    assert con_axon["strahler_max"] == 1


def test_procesar_carpeta_ordenado_ignora_no_swc_y_corruptos(tmp_path, capsys):
    for nombre in ["c.swc", "a.swc", "b.swc"]:
        escribir_swc(tmp_path / nombre, RAIZ_SIMPLE)
    (tmp_path / "notas.txt").write_text("no soy un swc")
    (tmp_path / "roto.swc").write_text("esto no es\nun swc valido 1 2\n")

    analizador = BiomarkerAnalyzer()
    assert analizador.procesar_carpeta(str(tmp_path), "sana") == 3
    assert [d["archivo"] for d in analizador.datos] == ["a.swc", "b.swc", "c.swc"]
    assert "Error al cargar roto.swc" in capsys.readouterr().out
