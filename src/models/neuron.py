# src/models/neuron.py
import morphio
import warnings
from ..utils.geometry import calcular_longitud_seccion

warnings.filterwarnings("ignore")

class Neurona:
    """
    Clase que representa una neurona con su morfologia.
    """
    
    def __init__(self, ruta_archivo, grupo):
        """
        Inicializa una neurona desde un archivo SWC.
        
        Args:
            ruta_archivo: ruta al archivo .swc
            grupo: 'sana' o 'alzheimer'
        """
        self.ruta_archivo = ruta_archivo
        self.nombre = ruta_archivo.split('/')[-1]
        self.grupo = grupo
        self._cargar_morfologia()
    
    def _cargar_morfologia(self):
        """Carga la morfologia desde el archivo."""
        try:
            self.morphology = morphio.Morphology(self.ruta_archivo)
            self.cargada = True
        except Exception as e:
            print(f"Error al cargar {self.nombre}: {e}")
            self.cargada = False
            self.morphology = None
    
    def calcular_strahler(self, section=None):
        """
        Calcula el orden de Strahler recursivamente.
        
        Args:
            section: seccion actual (None para comenzar desde raiz)
        
        Returns:
            int: orden de Strahler
        """
        if not self.cargada:
            return 0
        
        if section is None:
            if not self.morphology.sections:
                return 0
            section = self.morphology.sections[0]
        
        if not section.children:
            return 1
        
        child_orders = [self.calcular_strahler(child) for child in section.children]
        max_order = max(child_orders)
        
        if child_orders.count(max_order) >= 2:
            return max_order + 1
        
        return max_order
    
    def extraer_biomarcadores(self):
        """
        Extrae todos los biomarcadores de la neurona.
        
        Returns:
            dict: diccionario con los biomarcadores
        """
        if not self.cargada:
            return None
        
        bifurcaciones = 0
        terminales = 0
        longitud_total = 0.0
        
        for section in self.morphology.sections:
            longitud_total += calcular_longitud_seccion(section)
            if len(section.children) >= 2:
                bifurcaciones += 1
            if len(section.children) == 0:
                terminales += 1
        
        strahler_max = self.calcular_strahler()
        
        return {
            "archivo": self.nombre,
            "grupo": self.grupo,
            "puntos_totales": len(self.morphology.points),
            "secciones": len(self.morphology.sections),
            "longitud_total_um": round(longitud_total, 2),
            "bifurcaciones": bifurcaciones,
            "terminales": terminales,
            "strahler_max": strahler_max,
            "ratio_bifurcacion_terminal": round(
                bifurcaciones / terminales if terminales > 0 else 0, 3
            )
        }
    
    def obtener_tipos_seccion(self):
        """Obtiene los tipos de seccion presentes."""
        if not self.cargada:
            return set()
        
        tipos = set()
        for section in self.morphology.sections:
            tipos.add(str(section.type))
        
        return tipos