import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

class NeuronaClassifier:
    """
    Clasificador de neuronas (Sana vs Alzheimer) usando Random Forest.
    """
    
    def __init__(self, modelo_tipo="random_forest", random_state=42):
        """
        Inicializa el clasificador.
        
        Args:
            modelo_tipo: "random_forest", "svm", o "logistic"
            random_state: semilla para reproducibilidad
        """
        self.modelo_tipo = modelo_tipo
        self.random_state = random_state
        self.modelo = None
        self.scaler = None
        self.features = ["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]
        
        self._crear_modelo()
    
    def _crear_modelo(self):
        """Crea el modelo segun el tipo seleccionado."""
        if self.modelo_tipo == "random_forest":
            self.modelo = RandomForestClassifier(
                n_estimators=100,
                max_depth=4,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=self.random_state
            )
        elif self.modelo_tipo == "svm":
            self.modelo = SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                probability=True,
                random_state=self.random_state
            )
        elif self.modelo_tipo == "logistic":
            self.modelo = LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=self.random_state
            )
        else:
            raise ValueError(f"Modelo desconocido: {self.modelo_tipo}")
    
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
    
    def entrenar(self, X_train, y_train, escalar=False):
        """
        Entrena el modelo.
        
        Args:
            X_train: caracteristicas de entrenamiento
            y_train: etiquetas de entrenamiento
            escalar: si se debe escalar (necesario para SVM y Logistic)
        """
        if escalar:
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train)
        
        self.modelo.fit(X_train, y_train)
        print(f"Modelo {self.modelo_tipo} entrenado correctamente.")
    
    def predecir(self, X):
        """
        Predice la clase de una o varias neuronas.
        
        Args:
            X: caracteristicas de entrada
        
        Returns:
            predicciones (0=sana, 1=alzheimer)
        """
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        return self.modelo.predict(X)
    
    def predecir_proba(self, X):
        """
        Predice la probabilidad de pertenecer a cada clase.
        
        Args:
            X: caracteristicas de entrada
        
        Returns:
            probabilidades [prob_sana, prob_alzheimer]
        """
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        return self.modelo.predict_proba(X)
    
    def predecir_neurona(self, longitud, bifurcaciones, terminales, strahler):
        """
        Predice una neurona individual a partir de sus biomarcadores.
        
        Args:
            longitud: longitud total en micras
            bifurcaciones: numero de bifurcaciones
            terminales: numero de terminales
            strahler: orden de Strahler maximo
        
        Returns:
            dict con prediccion y probabilidades
        """
        X = np.array([[longitud, bifurcaciones, terminales, strahler]])
        
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        pred = self.modelo.predict(X)[0]
        proba = self.modelo.predict_proba(X)[0]
        
        return {
            "clase": "Alzheimer" if pred == 1 else "Sana",
            "probabilidad_sana": proba[0],
            "probabilidad_alzheimer": proba[1],
            "confianza": max(proba) * 100
        }
    
    def guardar(self, ruta):
        """Guarda el modelo entrenado en disco."""
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        joblib.dump({
            "modelo": self.modelo,
            "scaler": self.scaler,
            "modelo_tipo": self.modelo_tipo,
            "features": self.features
        }, ruta)
        print(f"Modelo guardado en: {ruta}")
    
    def cargar(self, ruta):
        """Carga un modelo previamente entrenado."""
        datos = joblib.load(ruta)
        self.modelo = datos["modelo"]
        self.scaler = datos["scaler"]
        self.modelo_tipo = datos["modelo_tipo"]
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