# src/processing/analyzer.py
import os
import pandas as pd
from ..models.neuron import Neurona

class BiomarkerAnalyzer:
    """
    Analizador de biomarcadores para multiples neuronas.
    """
    
    def __init__(self):
        self.datos = []
        self.df = None
    
    def procesar_carpeta(self, carpeta, grupo):
        """
        Procesa todos los archivos SWC en una carpeta.
        
        Args:
            carpeta: ruta a la carpeta
            grupo: 'sana' o 'alzheimer'
        
        Returns:
            int: numero de neuronas procesadas
        """
        contador = 0
        
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".swc"):
                ruta = os.path.join(carpeta, archivo)
                print(f"  Procesando: {archivo}")
                
                neurona = Neurona(ruta, grupo)
                biomarcadores = neurona.extraer_biomarcadores()
                
                if biomarcadores:
                    self.datos.append(biomarcadores)
                    contador += 1
                    print(f"    OK - {biomarcadores['puntos_totales']} puntos, {biomarcadores['bifurcaciones']} bifurcaciones")
        
        return contador
    
    def procesar_sanas(self, carpeta_sanas):
        """
        Procesa solo neuronas sanas.
        
        Args:
            carpeta_sanas: ruta a la carpeta de neuronas sanas
        
        Returns:
            int: numero de neuronas procesadas
        """
        return self.procesar_carpeta(carpeta_sanas, "sana")
    
    def generar_dataframe(self):
        """Genera DataFrame con todos los datos procesados."""
        if not self.datos:
            print("No hay datos para generar DataFrame.")
            return None
        
        self.df = pd.DataFrame(self.datos)
        return self.df
    
    def guardar_csv(self, ruta_salida):
        """Guarda el DataFrame en un archivo CSV."""
        if self.df is None:
            self.generar_dataframe()
        
        if self.df is not None:
            self.df.to_csv(ruta_salida, index=False)
            print(f"Dataset guardado: {ruta_salida}")
    
    def obtener_resumen(self):
        """Obtiene un resumen estadistico de los datos."""
        if self.df is None:
            return None
        
        resumen = {
            'total': len(self.df),
            'sanas': len(self.df[self.df['grupo'] == 'sana']),
            'alzheimer': len(self.df[self.df['grupo'] == 'alzheimer'])
        }
        
        return resumen
    
    def obtener_estadisticas_por_grupo(self):
        """Obtiene estadisticas agrupadas por grupo."""
        if self.df is None:
            return None
        
        columnas = ["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]
        return self.df.groupby("grupo")[columnas].agg(['mean', 'std', 'min', 'max'])