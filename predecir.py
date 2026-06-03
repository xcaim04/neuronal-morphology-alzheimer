import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.classification.classifier import NeuronaClassifier

def predecir_desde_csv(ruta_entrada, ruta_salida=None, modelo_path="./modelos/clasificador_neurona.pkl"):
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
    
    if not os.path.exists(modelo_path):
        raise FileNotFoundError(f"No se encuentra el modelo: {modelo_path}")
    
    # Cargar modelo
    clasificador = NeuronaClassifier()
    clasificador.cargar(modelo_path)
    
    # Cargar datos
    df = pd.read_csv(ruta_entrada)
    
    columnas_necesarias = ["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]
    columnas_faltantes = [col for col in columnas_necesarias if col not in df.columns]
    
    if columnas_faltantes:
        raise ValueError(f"Columnas faltantes en el CSV: {columnas_faltantes}")
    
    # Predecir cada fila
    predicciones = []
    probabilidades_sana = []
    probabilidades_alzheimer = []
    confianzas = []
    
    for _, row in df.iterrows():
        resultado = clasificador.predecir_neurona(
            longitud=row["longitud_total_um"],
            bifurcaciones=row["bifurcaciones"],
            terminales=row["terminales"],
            strahler=row["strahler_max"]
        )
        predicciones.append(resultado["clase"])
        probabilidades_sana.append(resultado["probabilidad_sana"])
        probabilidades_alzheimer.append(resultado["probabilidad_alzheimer"])
        confianzas.append(resultado["confianza"])
    
    # Añadir columnas al DataFrame
    df["prediccion"] = predicciones
    df["probabilidad_sana"] = probabilidades_sana
    df["probabilidad_alzheimer"] = probabilidades_alzheimer
    df["confianza_porcentaje"] = confianzas
    
    # Guardar si se especifica ruta de salida
    if ruta_salida:
        df.to_csv(ruta_salida, index=False)
        print(f"Predicciones guardadas en: {ruta_salida}")
    
    return df

def predecir_desde_dataframe(df, modelo_path="./modelos/clasificador_neurona.pkl"):
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
    
    predicciones = []
    probabilidades_sana = []
    probabilidades_alzheimer = []
    confianzas = []
    
    for _, row in df.iterrows():
        resultado = clasificador.predecir_neurona(
            longitud=row["longitud_total_um"],
            bifurcaciones=row["bifurcaciones"],
            terminales=row["terminales"],
            strahler=row["strahler_max"]
        )
        predicciones.append(resultado["clase"])
        probabilidades_sana.append(resultado["probabilidad_sana"])
        probabilidades_alzheimer.append(resultado["probabilidad_alzheimer"])
        confianzas.append(resultado["confianza"])
    
    df["prediccion"] = predicciones
    df["probabilidad_sana"] = probabilidades_sana
    df["probabilidad_alzheimer"] = probabilidades_alzheimer
    df["confianza_porcentaje"] = confianzas
    
    return df

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clasificador de neuronas")
    parser.add_argument("entrada", help="Ruta al archivo CSV de entrada")
    parser.add_argument("-s", "--salida", help="Ruta al archivo CSV de salida", default=None)
    parser.add_argument("-m", "--modelo", help="Ruta al modelo entrenado", default="./modelos/clasificador_neurona.pkl")
    
    args = parser.parse_args()
    
    try:
        df_resultado = predecir_desde_csv(args.entrada, args.salida, args.modelo)
        
        print("\nResumen de predicciones:")
        print(df_resultado["prediccion"].value_counts())
        print(f"\nConfianza media: {df_resultado['confianza_porcentaje'].mean():.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")