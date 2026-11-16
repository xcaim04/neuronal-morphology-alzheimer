import json
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODELO_PATH, RESULTADOS_EVALUACION
from src.classification.classifier import NeuronaClassifier

def aviso_azar():
    """Texto de aviso si el modelo no supera el azar según el informe de evaluación; None si lo supera o no hay informe."""
    ruta = os.path.join(RESULTADOS_EVALUACION, "informe_evaluacion.json")
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        metricas = json.load(f)["resultados"]["RandomForest"]
    auc, acc = metricas["auc"], metricas["accuracy"]
    if auc["mean"] - auc["std"] > 0.5:
        return None
    return (
        f"El modelo no supera el azar (AUC {auc['mean']:.2f} ± {auc['std']:.2f}, "
        f"accuracy {acc['mean']:.2f} ± {acc['std']:.2f} en validación cruzada): sus predicciones no tienen valor."
    )

def predecir_desde_csv(ruta_entrada, ruta_salida=None, modelo_path=MODELO_PATH):
    """
    Predice la clasificacion de neuronas desde un archivo CSV.

    El CSV de entrada debe contener las columnas:
        longitud_total_um, bifurcaciones, terminales, strahler_max

    Args:
        ruta_entrada: ruta al archivo CSV con los datos
        ruta_salida: ruta donde guardar el CSV con predicciones (opcional)
        modelo_path: ruta al modelo entrenado

    Returns:
        DataFrame con las predicciones añadidas
    """
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No se encuentra el archivo: {ruta_entrada}")

    df = predecir_desde_dataframe(pd.read_csv(ruta_entrada), modelo_path)

    # Guardar si se especifica ruta de salida
    if ruta_salida:
        df.to_csv(ruta_salida, index=False)
        print(f"Predicciones guardadas en: {ruta_salida}")

    return df

def predecir_desde_dataframe(df, modelo_path=MODELO_PATH):
    """
    Predice desde un DataFrame directamente.

    Args:
        df: DataFrame con columnas longitud_total_um, bifurcaciones, terminales, strahler_max
        modelo_path: ruta al modelo entrenado

    Returns:
        DataFrame con las predicciones añadidas
    """
    if not os.path.exists(modelo_path):
        raise FileNotFoundError(f"No se encuentra el modelo: {modelo_path}")

    clasificador = NeuronaClassifier()
    clasificador.cargar(modelo_path)

    columnas_faltantes = [col for col in clasificador.features if col not in df.columns]
    if columnas_faltantes:
        raise ValueError(f"Columnas faltantes: {columnas_faltantes}")

    # El modelo se entreno con arrays sin nombres de columna.
    X = df[clasificador.features].to_numpy()
    proba = clasificador.predecir_proba(X)

    df["prediccion"] = ["Alzheimer" if p == 1 else "Sana" for p in clasificador.predecir(X)]
    df["probabilidad_sana"] = proba[:, 0]
    df["probabilidad_alzheimer"] = proba[:, 1]
    df["confianza_porcentaje"] = proba.max(axis=1) * 100

    return df

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clasificador de neuronas")
    parser.add_argument("entrada", help="Ruta al archivo CSV de entrada")
    parser.add_argument("-s", "--salida", help="Ruta al archivo CSV de salida", default=None)
    parser.add_argument("-m", "--modelo", help="Ruta al modelo entrenado", default=MODELO_PATH)

    args = parser.parse_args()

    try:
        df_resultado = predecir_desde_csv(args.entrada, args.salida, args.modelo)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"Error: {e}")

    aviso = aviso_azar()
    if aviso:
        print(f"AVISO: {aviso}", file=sys.stderr)

    print("\nResumen de predicciones:")
    print(df_resultado["prediccion"].value_counts())
    print(f"\nConfianza media: {df_resultado['confianza_porcentaje'].mean():.1f}%")
