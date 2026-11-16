import os
import sys
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RESULTADOS_SANAS, RESULTADOS_ALZHEIMER, RESULTADOS_EVALUACION, MODELO_PATH
from src.classification.classifier import NeuronaClassifier
from src.classification.evaluator import Evaluador
from src.processing.storage import BiomarkerStore

def cargar_datos():
    """Carga los datasets de sanas y enfermas."""
    ruta_sanas = os.path.join(RESULTADOS_SANAS, "dataset_biomarcadores.csv")
    ruta_enfermas = os.path.join(RESULTADOS_ALZHEIMER, "dataset_biomarcadores.csv")

    if not os.path.exists(ruta_sanas):
        raise FileNotFoundError(f"No se encuentra {ruta_sanas}")

    if not os.path.exists(ruta_enfermas):
        raise FileNotFoundError(f"No se encuentra {ruta_enfermas}")

    df_sanas = pd.read_csv(ruta_sanas)
    df_enfermas = pd.read_csv(ruta_enfermas)

    print(f"Datos cargados:")
    print(f"  - Sanas: {len(df_sanas)} neuronas")
    print(f"  - Enfermas: {len(df_enfermas)} neuronas")

    return df_sanas, df_enfermas

def main():
    print("=" * 60)
    print("ENTRENAMIENTO DE CLASIFICADOR DE NEURONAS")
    print("=" * 60)

    # Cargar datos
    df_sanas, df_enfermas = cargar_datos()

    # Preparar clasificador
    clasificador = NeuronaClassifier()

    # Preparar datos (X, y)
    X, y, df_combinado = clasificador.preparar_datos(df_sanas, df_enfermas)

    print(f"\nCaracteristicas:")
    for i, feat in enumerate(clasificador.features):
        print(f"  - {feat}")

    # Con tan pocas muestras un hold-out no dice nada: la metrica principal es la CV repetida.
    print("\n" + "=" * 60)
    print("VALIDACION CRUZADA")
    print("=" * 60)
    evaluador = Evaluador(output_dir=RESULTADOS_EVALUACION)
    resultados_cv = evaluador.evaluar(clone(clasificador.modelo), X, y, "RandomForest")
    resultados_base = evaluador.validacion_cruzada(
        DummyClassifier(strategy="most_frequent"), X, y, "LineaBase"
    )

    # Modelo final: todos los datos
    print("\nEntrenando modelo final con todos los datos...")
    clasificador.entrenar(X, y)

    # Importancia de caracteristicas
    print("\n" + "=" * 60)
    print("IMPORTANCIA DE CARACTERISTICAS")
    print("=" * 60)

    importancia = clasificador.obtener_importancia()
    if importancia is not None:
        print(importancia.to_string(index=False))
        importancia.to_csv(os.path.join(RESULTADOS_EVALUACION, "importancia_caracteristicas.csv"), index=False)

    # Guardar modelo entrenado
    clasificador.guardar(MODELO_PATH)

    n_sanas, n_alzheimer = (int(n) for n in np.bincount(y, minlength=2))
    evaluador.generar_informe(
        n_por_clase={"sana": n_sanas, "alzheimer": n_alzheimer},
        hiperparametros=clasificador.modelo.get_params(),
        features=clasificador.features,
    )
    BiomarkerStore().save_training_run(
        model_name="RandomForest",
        sample_count=len(y),
        healthy_count=n_sanas,
        alzheimer_count=n_alzheimer,
        metrics={"cv": resultados_cv, "linea_base": resultados_base},
        features=clasificador.features,
    )

    # Probar prediccion en neuronas tipicas
    print("\n" + "=" * 60)
    print("EJEMPLO DE PREDICCION")
    print("=" * 60)

    ejemplos = {
        "Neurona Sana tipica": [3500, 50, 55, 3],
        "Neurona Alzheimer tipica": [2000, 10, 15, 2],
    }
    probas = clasificador.predecir_proba(np.array(list(ejemplos.values())))
    for nombre, proba in zip(ejemplos, probas):
        print(f"\n{nombre}:")
        print(f"  Prediccion: {'Alzheimer' if proba[1] > 0.5 else 'Sana'}")
        print(f"  Confianza: {proba.max() * 100:.1f}%")
        print(f"  Prob Sana: {proba[0]:.3f}")
        print(f"  Prob Alzheimer: {proba[1]:.3f}")

    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print("\nArchivos generados:")
    print(f"  - {MODELO_PATH}")
    for archivo in ["metricas_RandomForest.csv", "matriz_confusion_RandomForest.png",
                    "curva_roc_RandomForest.png", "importancia_caracteristicas.csv",
                    "informe_evaluacion.json"]:
        print(f"  - {os.path.join(RESULTADOS_EVALUACION, archivo)}")

if __name__ == "__main__":
    main()
