import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class NeuronaClassifier:
    """
    Clasificador de neuronas (Sana vs Alzheimer) usando Random Forest.
    """
    
    def __init__(self, random_state=42):
        """
        Inicializa el clasificador.
        
        Args:
            random_state: semilla para reproducibilidad
        """
        self.random_state = random_state
        self.features = ["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=4,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=random_state
        )
    
    def preparar_datos(self, df_sanas, df_enfermas):
        """
        Prepara los datos para entrenamiento.
        
        Args:
            df_sanas: DataFrame de neuronas sanas
            df_enfermas: DataFrame de neuronas con Alzheimer
        
        Returns:
            X, y: caracteristicas y etiquetas
        """
        # Copiar para no modificar originales
        df_s = df_sanas.copy()
        df_e = df_enfermas.copy()
        
        # Asignar etiquetas
        df_s["target"] = 0  # sana
        df_e["target"] = 1  # alzheimer
        
        # Combinar
        df_combinado = pd.concat([df_s, df_e], ignore_index=True)
        
        # Seleccionar caracteristicas
        X = df_combinado[self.features].values
        y = df_combinado["target"].values
        
        return X, y, df_combinado
    
    def entrenar(self, X_train, y_train):
        """Entrena el modelo."""
        self.modelo.fit(X_train, y_train)
        print("Modelo RandomForest entrenado correctamente.")
    
    def predecir(self, X):
        """Predice la clase (0=sana, 1=alzheimer) de una o varias neuronas."""
        return self.modelo.predict(X)
    
    def predecir_proba(self, X):
        """Devuelve las probabilidades [prob_sana, prob_alzheimer] de cada neurona."""
        return self.modelo.predict_proba(X)
    
    def guardar(self, ruta):
        """Guarda el modelo entrenado en disco."""
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        joblib.dump({
            "modelo": self.modelo,
            "features": self.features
        }, ruta)
        print(f"Modelo guardado en: {ruta}")
    
    def cargar(self, ruta):
        """Carga un modelo previamente entrenado."""
        datos = joblib.load(ruta)
        # Los .pkl antiguos traen ademas "scaler" (siempre None) y "modelo_tipo"; se ignoran.
        self.modelo = datos["modelo"]
        self.features = datos["features"]
        print(f"Modelo cargado desde: {ruta}")
    
    def obtener_importancia(self, feature_names=None):
        """
        Obtiene la importancia de cada caracteristica (solo Random Forest).
        """
        if feature_names is None:
            feature_names = self.features
        
        if hasattr(self.modelo, "feature_importances_"):
            importancia = pd.DataFrame({
                "caracteristica": feature_names,
                "importancia": self.modelo.feature_importances_
            }).sort_values("importancia", ascending=False)
            return importancia
        else:
            print("Este modelo no soporta importancia de caracteristicas.")
            return None