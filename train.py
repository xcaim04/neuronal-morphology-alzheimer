# train.py
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RESULTADOS_SANAS, RESULTADOS_ALZHEIMER
from src.classification.classifier import NeuronaClassifier
from src.classification.evaluator import Evaluador

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
    clasificador = NeuronaClassifier(modelo_tipo="random_forest")
    
    # Preparar datos (X, y)
    X, y, df_combinado = clasificador.preparar_datos(df_sanas, df_enfermas)
    
    print(f"\nCaracteristicas:")
    for i, feat in enumerate(clasificador.features):
        print(f"  - {feat}")
    
    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"\nDivision de datos:")
    print(f"  - Entrenamiento: {len(X_train)} muestras")
    print(f"  - Prueba: {len(X_test)} muestras")
    
    # Entrenar modelo
    print("\nEntrenando modelo...")
    clasificador.entrenar(X_train, y_train, escalar=False)
    
    # Evaluar
    evaluador = Evaluador(output_dir="./resultados/evaluacion")
    
    # Evaluar en test
    metricas = evaluador.evaluar(clasificador.modelo, X_test, y_test, "RandomForest")
    
    # Validacion cruzada (importante con pocos datos)
    print("\n" + "=" * 60)
    print("VALIDACION CRUZADA")
    print("=" * 60)
    
    # Recrear modelo para CV
    from sklearn.ensemble import RandomForestClassifier
    modelo_cv = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42)
    resultados_cv = evaluador.validacion_cruzada(modelo_cv, X, y, cv=5, nombre_modelo="RandomForest")
    
    # Importancia de caracteristicas
    print("\n" + "=" * 60)
    print("IMPORTANCIA DE CARACTERISTICAS")
    print("=" * 60)
    
    importancia = clasificador.obtener_importancia()
    if importancia is not None:
        print(importancia.to_string(index=False))
        
        # Guardar importancia
        importancia.to_csv("./resultados/evaluacion/importancia_caracteristicas.csv", index=False)
    
    # Guardar modelo entrenado
    clasificador.guardar("./modelos/clasificador_neurona.pkl")
    
    # Probar prediccion en una neurona nueva
    print("\n" + "=" * 60)
    print("EJEMPLO DE PREDICCION")
    print("=" * 60)
    
    # Valores tipicos de una neurona sana
    print("\nNeurona Sana tipica:")
    prediccion = clasificador.predecir_neurona(
        longitud=3500,
        bifurcaciones=50,
        terminales=55,
        strahler=3
    )
    print(f"  Prediccion: {prediccion['clase']}")
    print(f"  Confianza: {prediccion['confianza']:.1f}%")
    print(f"  Prob Sana: {prediccion['probabilidad_sana']:.3f}")
    print(f"  Prob Alzheimer: {prediccion['probabilidad_alzheimer']:.3f}")
    
    print("\nNeurona Alzheimer tipica:")
    prediccion = clasificador.predecir_neurona(
        longitud=2000,
        bifurcaciones=10,
        terminales=15,
        strahler=2
    )
    print(f"  Prediccion: {prediccion['clase']}")
    print(f"  Confianza: {prediccion['confianza']:.1f}%")
    print(f"  Prob Sana: {prediccion['probabilidad_sana']:.3f}")
    print(f"  Prob Alzheimer: {prediccion['probabilidad_alzheimer']:.3f}")
    
    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print("\nArchivos generados:")
    print("  - ./modelos/clasificador_neurona.pkl")
    print("  - ./resultados/evaluacion/matriz_confusion_RandomForest.png")
    print("  - ./resultados/evaluacion/curva_roc_RandomForest.png")
    print("  - ./resultados/evaluacion/importancia_caracteristicas.csv")
    print("  - ./resultados/evaluacion/informe_evaluacion.json")

if __name__ == "__main__":
    main()