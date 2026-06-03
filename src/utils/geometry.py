# src/utils/geometry.py
import math

def calcular_distancia_euclidiana(p1, p2):
    """
    Calcula distancia euclidiana entre dos puntos 3D.
    
    Args:
        p1: primer punto (x, y, z)
        p2: segundo punto (x, y, z)
    
    Returns:
        float: distancia en micrómetros
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def calcular_longitud_seccion(section):
    """
    Calcula la longitud total de una seccion.
    
    Args:
        section: seccion de morphio
    
    Returns:
        float: longitud en micrómetros
    """
    puntos = section.points
    if len(puntos) < 2:
        return 0.0
    
    longitud = 0.0
    for i in range(len(puntos) - 1):
        longitud += calcular_distancia_euclidiana(puntos[i], puntos[i+1])
    
    return longitud