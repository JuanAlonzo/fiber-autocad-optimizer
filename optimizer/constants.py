"""
Constantes del Sistema.
Agrupadas por contexto para evitar imports masivos y facilitar el autocompletado.
"""


class ASI:
    """AutoCAD Color Index (Colores estándar)"""

    ROJO = 1
    AMARILLO = 2
    VERDE = 3
    CYAN = 4
    AZUL = 5
    MAGENTA = 6
    BLANCO = 7
    GRIS = 8


class SysLayers:
    """Capas internas gestionadas por el sistema (No configurables por usuario)"""

    DEBUG_NODOS = "DEBUG_GRAFO_NODOS"
    DEBUG_ARISTAS = "DEBUG_GRAFO_ARISTAS"
    DEBUG_RUTAS = "DEBUG_RUTAS_CALCULADAS"
    ERRORES = "ERRORES_TOPOLOGIA"
    TEMPORAL_EXTREMOS = "DEBUG_DIRECCION_TRAMOS"
    TEXTO_TRAMOS = "TEXTO_TRAMOS"
    TEXTO_RESERVAS = "TEXTO_RESERVAS"


class Geometry:
    """Valores geométricos fijos del sistema"""

    RADIO_NODO = 0.2
    RADIO_ERROR = 5.0
    RADIO_SNAP_DEFECTO = 5.0
    RADIO_INI_FIN = 1.0
    OFFSET_RUTAS = 0.5
    TEXT_ALIGNMENT_CENTER = 13
    TEXT_HEIGHT = 1.0
