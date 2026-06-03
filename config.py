import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
SANAS_DIR = os.path.join(DATASET_DIR, "sanas")
ALZHEIMER_DIR = os.path.join(DATASET_DIR, "enfermas")
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados")

RESULTADOS_SANAS = os.path.join(RESULTADOS_DIR, "sanas")
RESULTADOS_ALZHEIMER = os.path.join(RESULTADOS_DIR, "alzheimer")
RESULTADOS_COMPARATIVA = os.path.join(RESULTADOS_DIR, "comparativa")

BIOMARCADORES = [
    "puntos_totales",
    "secciones",
    "longitud_total_um",
    "bifurcaciones",
    "terminales",
    "strahler_max",
    "ratio_bifurcacion_terminal"
]

PLOT_STYLE = "whitegrid"
COLORES = {
    "sana": "green",
    "alzheimer": "red"
}
DPI = 150