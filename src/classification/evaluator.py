import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import (
    RepeatedStratifiedKFold, StratifiedKFold, cross_validate, cross_val_predict
)
from sklearn.metrics import (
    make_scorer, precision_score, confusion_matrix, classification_report,
    roc_curve, roc_auc_score
)
import seaborn as sns

from config import RESULTADOS_EVALUACION

# La linea base nunca predice la clase positiva: sin zero_division avisaria en cada pliegue.
SCORERS = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": "recall",
    "f1": "f1",
    "auc": "roc_auc",
}


def _n_splits(y, maximo=5):
    """Pliegues posibles sin dejar un pliegue sin muestras de la clase minoritaria."""
    minoritaria = int(np.bincount(y).min())
    if minoritaria < 2:
        raise ValueError(f"Se necesitan al menos 2 muestras por clase (hay {minoritaria})")
    return min(maximo, minoritaria)


class Evaluador:
    """
    Evaluador de modelos de clasificacion mediante validacion cruzada.
    """

    def __init__(self, output_dir=RESULTADOS_EVALUACION):
        self.output_dir = output_dir
        self.resultados = {}
        os.makedirs(output_dir, exist_ok=True)

    def validacion_cruzada(self, modelo, X, y, nombre_modelo="Modelo", n_repeats=10):
        """
        Validacion cruzada estratificada repetida con todas las metricas en una pasada.

        Returns:
            dict metrica -> {"mean", "std"} (floats nativos)
        """
        n_splits = _n_splits(y)
        cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=42)
        scores = cross_validate(modelo, X, y, cv=cv, scoring=SCORERS)

        resultados_cv = {
            m: {"mean": float(scores[f"test_{m}"].mean()), "std": float(scores[f"test_{m}"].std())}
            for m in SCORERS
        }
        self.resultados[nombre_modelo] = resultados_cv

        print(f"\n{'='*50}")
        print(f"Validacion Cruzada ({n_splits} pliegues x {n_repeats} repeticiones) - {nombre_modelo}")
        print(f"{'='*50}")
        for m, r in resultados_cv.items():
            print(f"{m:<10} {r['mean']:.4f} (+/- {r['std']:.4f})")

        return resultados_cv

    def evaluar(self, modelo, X, y, nombre_modelo="Modelo"):
        """
        Validacion cruzada repetida + matriz de confusion y curva ROC out-of-fold.
        Guarda metricas_<modelo>.csv y las graficas.
        """
        resultados_cv = self.validacion_cruzada(modelo, X, y, nombre_modelo)

        # cross_val_predict exige una particion: un solo KFold, no el repetido.
        cv = StratifiedKFold(n_splits=_n_splits(y), shuffle=True, random_state=42)
        y_proba = cross_val_predict(modelo, X, y, cv=cv, method="predict_proba")[:, 1]
        y_pred = (y_proba > 0.5).astype(int)

        print(f"\nReporte de Clasificacion (out-of-fold):")
        print(classification_report(y, y_pred, target_names=["Sana", "Alzheimer"], zero_division=0))

        self._guardar_metricas(nombre_modelo, resultados_cv)
        self._graficar_matriz_confusion(y, y_pred, nombre_modelo)
        self._graficar_curva_roc(y, y_proba, nombre_modelo, roc_auc_score(y, y_proba))

        return resultados_cv

    def _graficar_matriz_confusion(self, y_true, y_pred, nombre_modelo):
        """Genera y guarda la matriz de confusion."""
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Sana', 'Alzheimer'],
                    yticklabels=['Sana', 'Alzheimer'])
        plt.xlabel('Prediccion')
        plt.ylabel('Real')
        plt.title(f'Matriz de Confusion (out-of-fold) - {nombre_modelo}')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/matriz_confusion_{nombre_modelo.replace(' ', '_')}.png", dpi=150)
        plt.close()

    def _graficar_curva_roc(self, y_true, y_pred_proba, nombre_modelo, auc):
        """Genera y guarda la curva ROC."""
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, 'b-', label=f'{nombre_modelo} (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], 'r--', label='Clasificador Aleatorio')
        plt.xlabel('Tasa de Falsos Positivos')
        plt.ylabel('Tasa de Verdaderos Positivos')
        plt.title(f'Curva ROC (out-of-fold) - {nombre_modelo}')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/curva_roc_{nombre_modelo.replace(' ', '_')}.png", dpi=150)
        plt.close()

    def _guardar_metricas(self, nombre_modelo, resultados_cv):
        """Guarda media y desviacion de cada metrica en un CSV."""
        df = pd.DataFrame(resultados_cv).T.rename_axis("metrica").reset_index()
        df.to_csv(f"{self.output_dir}/metricas_{nombre_modelo.replace(' ', '_')}.csv", index=False)

    def generar_informe(self, **extra):
        """Genera informe_evaluacion.json con los resultados y los datos extra (deben ser tipos nativos)."""
        informe = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resultados": self.resultados,
            **extra,
        }

        ruta = f"{self.output_dir}/informe_evaluacion.json"
        with open(ruta, "w") as f:
            json.dump(informe, f, indent=4)

        print(f"\nInforme guardado en: {ruta}")
