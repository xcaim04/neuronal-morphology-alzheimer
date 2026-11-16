# src/models/neuron.py
import os
import morphio
from ..utils.geometry import calcular_longitud_seccion

# morphio emite "Three Point Soma" en casi todos los SWC de NeuroMorpho; es ruido, no un error de datos.
morphio.set_ignored_warning(morphio.Warning.soma_non_conform, True)

TIPOS_DENDRITA = (morphio.SectionType.basal_dendrite, morphio.SectionType.apical_dendrite)

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
        self.nombre = os.path.basename(ruta_archivo)
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
            section: seccion actual (None para el maximo sobre todas las raices dendriticas)
        
        Returns:
            int: orden de Strahler
        """
        if not self.cargada:
            return 0
        
        if section is None:
            raices = [s for s in self.morphology.root_sections if s.type in TIPOS_DENDRITA]
            return max((self.calcular_strahler(s) for s in raices), default=0)
        
        if not section.children:
            return 1
        
        child_orders = [self.calcular_strahler(child) for child in section.children]
        max_order = max(child_orders)
        
        if child_orders.count(max_order) >= 2:
            return max_order + 1
        
        return max_order
    
    def extraer_biomarcadores(self):
        """
        Extrae los biomarcadores dendriticos (basales y apicales) de la neurona.
        
        Returns:
            dict: diccionario con los biomarcadores
        """
        if not self.cargada:
            return None
        
        bifurcaciones = 0
        terminales = 0
        longitud_total = 0.0
        puntos = 0
        secciones = 0
        
        for section in self.morphology.iter():
            if section.type not in TIPOS_DENDRITA:
                continue
            secciones += 1
            puntos += len(section.points)
            longitud_total += calcular_longitud_seccion(section)
            if len(section.children) >= 2:
                bifurcaciones += 1
            if len(section.children) == 0:
                terminales += 1
        
        strahler_max = self.calcular_strahler()
        
        return {
            "archivo": self.nombre,
            "grupo": self.grupo,
            "puntos_totales": puntos,
            "secciones": secciones,
            "longitud_total_um": round(longitud_total, 2),
            "bifurcaciones": bifurcaciones,
            "terminales": terminales,
            "strahler_max": strahler_max,
            "ratio_bifurcacion_terminal": round(
                bifurcaciones / terminales if terminales > 0 else 0, 3
            )
        }
