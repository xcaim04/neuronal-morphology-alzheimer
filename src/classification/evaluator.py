import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, roc_auc_score
)
import seaborn as sns

class Evaluador:
    """
    Evaluador de modelos de clasificacion.
    """
    
    def __init__(self, output_dir="./resultados/evaluacion"):
        self.output_dir = output_dir
        self.resultados = {}
        
        import os
        os.makedirs(output_dir, exist_ok=True)
    
    def evaluar(self, modelo, X_test, y_test, nombre_modelo="Modelo"):
        """
        Evalua el modelo en datos de prueba.
        
        Returns:
            dict con todas las metricas
        """
        y_pred = modelo.predict(X_test)
        y_pred_proba = modelo.predict_proba(X_test)[:, 1]
        
        metricas = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "auc": roc_auc_score(y_test, y_pred_proba)
        }
        
        self.resultados[nombre_modelo] = metricas
        
        # Imprimir resultados
        print(f"\n{'='*50}")
        print(f"Evaluacion de {nombre_modelo}")
        print(f"{'='*50}")
        print(f"Accuracy:  {metricas['accuracy']:.4f}")
        print(f"Precision: {metricas['precision']:.4f}")
        print(f"Recall:    {metricas['recall']:.4f}")
        print(f"F1-Score:  {metricas['f1_score']:.4f}")
        print(f"AUC-ROC:   {metricas['auc']:.4f}")
        
        print(f"\nReporte de Clasificacion:")
        print(classification_report(y_test, y_pred, target_names=["Sana", "Alzheimer"]))
        
        # Guardar metricas
        self._guardar_metricas(nombre_modelo, metricas)
        
        # Generar graficas
        self._graficar_matriz_confusion(y_test, y_pred, nombre_modelo)
        self._graficar_curva_roc(y_test, y_pred_proba, nombre_modelo, metricas["auc"])
        
        return metricas
    
    def validacion_cruzada(self, modelo, X, y, cv=5, nombre_modelo="Modelo"):
        """
        Realiza validacion cruzada.
        
        Args:
            modelo: modelo a evaluar (no entrenado)
            X: caracteristicas completas
            y: etiquetas completas
            cv: numero de pliegues
        
        Returns:
            puntuaciones medias y std
        """
        # Usar StratifiedKFold para mantener proporcion de clases
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        scores_acc = cross_val_score(modelo, X, y, cv=skf, scoring='accuracy')
        scores_precision = cross_val_score(modelo, X, y, cv=skf, scoring='precision')
        scores_recall = cross_val_score(modelo, X, y, cv=skf, scoring='recall')
        scores_f1 = cross_val_score(modelo, X, y, cv=skf, scoring='f1')
        
        print(f"\n{'='*50}")
        print(f"Validacion Cruzada ({cv} pliegues) - {nombre_modelo}")
        print(f"{'='*50}")
        print(f"Accuracy:  {scores_acc.mean():.4f} (+/- {scores_acc.std():.4f})")
        print(f"Precision: {scores_precision.mean():.4f} (+/- {scores_precision.std():.4f})")
        print(f"Recall:    {scores_recall.mean():.4f} (+/- {scores_recall.std():.4f})")
        print(f"F1-Score:  {scores_f1.mean():.4f} (+/- {scores_f1.std():.4f})")
        
        resultados_cv = {
            "accuracy": {"mean": scores_acc.mean(), "std": scores_acc.std()},
            "precision": {"mean": scores_precision.mean(), "std": scores_precision.std()},
            "recall": {"mean": scores_recall.mean(), "std": scores_recall.std()},
            "f1": {"mean": scores_f1.mean(), "std": scores_f1.std()}
        }
        
        return resultados_cv
    
    def comparar_modelos(self, modelos_dict, X_train, X_test, y_train, y_test):
        """
        Compara multiples modelos.
        
        Args:
            modelos_dict: dict con nombre -> modelo
        """
        print("\n" + "="*60)
        print("COMPARACION DE MODELOS")
        print("="*60)
        
        resultados = {}
        
        for nombre, modelo in modelos_dict.items():
            # Entrenar
            modelo.fit(X_train, y_train)
            
            # Evaluar
            y_pred = modelo.predict(X_test)
            y_pred_proba = modelo.predict_proba(X_test)[:, 1]
            
            resultados[nombre] = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
                "auc": roc_auc_score(y_test, y_pred_proba)
            }
            
            print(f"\n{nombre}:")
            print(f"  Accuracy: {resultados[nombre]['accuracy']:.4f}")
            print(f"  F1-Score: {resultados[nombre]['f1']:.4f}")
            print(f"  AUC:      {resultados[nombre]['auc']:.4f}")
        
        # Graficar comparacion
        self._graficar_comparacion_modelos(resultados)
        
        return resultados
    
    def _graficar_matriz_confusion(self, y_true, y_pred, nombre_modelo):
        """Genera y guarda la matriz de confusion."""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Sana', 'Alzheimer'],
                    yticklabels=['Sana', 'Alzheimer'])
        plt.xlabel('Prediccion')
        plt.ylabel('Real')
        plt.title(f'Matriz de Confusion - {nombre_modelo}')
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
        plt.title(f'Curva ROC - {nombre_modelo}')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/curva_roc_{nombre_modelo.replace(' ', '_')}.png", dpi=150)
        plt.close()
    
    def _graficar_comparacion_modelos(self, resultados):
        """Grafica comparativa de modelos."""
        metricas = ['accuracy', 'precision', 'recall', 'f1', 'auc']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(metricas))
        width = 0.8 / len(resultados)
        
        colores = ['#2ecc71', '#e74c3c', '#3498db']
        
        for i, (nombre, metricas_dict) in enumerate(resultados.items()):
            valores = [metricas_dict[m] for m in metricas]
            offset = (i - len(resultados)/2) * width + width/2
            ax.bar(x + offset, valores, width, label=nombre, color=colores[i % len(colores)])
        
        ax.set_xlabel('Metricas')
        ax.set_ylabel('Puntuacion')
        ax.set_title('Comparacion de Modelos')
        ax.set_xticks(x)
        ax.set_xticklabels(metricas)
        ax.legend(loc='lower right')
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/comparacion_modelos.png", dpi=150)
        plt.close()
    
    def _guardar_metricas(self, nombre_modelo, metricas):
        """Guarda las metricas en un archivo CSV."""
        df = pd.DataFrame([metricas])
        df.to_csv(f"{self.output_dir}/metricas_{nombre_modelo.replace(' ', '_')}.csv", index=False)
    
    def generar_informe(self):
        """Genera un informe resumen de todas las evaluaciones."""
        import json
        from datetime import datetime
        
        informe = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resultados": self.resultados
        }
        
        with open(f"{self.output_dir}/informe_evaluacion.json", "w") as f:
            json.dump(informe, f, indent=4)
        
        print(f"\nInforme guardado en: {self.output_dir}/informe_evaluacion.json")