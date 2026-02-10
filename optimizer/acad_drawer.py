"""
Módulo de Dibujo (Drawer).
Contiene funciones puras para dibujar entidades de diagnóstico en AutoCAD.
No realiza cálculos de ruta, solo visualización.
"""

from typing import List, Tuple, Optional, Any
import win32com.client
import pythoncom
from .config_loader import get_config
from .feedback_logger import logger

DISTANCE = get_config("rutas.offset_visual_debug", 0.5)
LAYER_DEBUG = get_config("rutas.capa_debug", "DEBUG_RUTAS")
COLOR_ERROR = get_config("visualizacion.color_error", 1)  # Rojo
COLOR_DEBUG = get_config("visualizacion.color_debug", 6)  # Magenta
RADIO_ERROR = get_config("visualizacion.radio_error", 5.0)
COLOR_GRAFO = get_config("visualizacion.color_grafo", 8)  # Gris
RADIO_NODO = get_config("visualizacion.radio_nodo_debug", 0.2)


def dibujar_debug_offset(
    msp: Any, puntos: List[Tuple[float, float]], color: Optional[int] = None
) -> None:
    """
    Dibuja una polilínea visual (offset) paralela a la ruta calculada.
    Útil para verificar visualmente el camino sin solapar la línea original.

    Args:
        msp (Any): Objeto ModelSpace de AutoCAD.
        puntos (List[Tuple[float, float]]): Lista de coordenadas [(x,y), (x,y)...].
        color (Optional[int]): Índice de color ACI (AutoCAD Color Index).
    """
    if not puntos or len(puntos) < 2:
        return

    if color is None:
        color = COLOR_DEBUG

    # Aplanar lista de puntos para el formato que exige win32com
    vertices = []
    for p in puntos:
        vertices.extend([p[0], p[1]])

    try:
        var_pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, vertices)
        pline = msp.AddLightWeightPolyline(var_pt)

        # Intentar realizar offset geométrico
        try:
            objs = pline.Offset(DISTANCE)
            pline.Delete()
            final_obj = objs[0]
        except Exception:
            final_obj = pline  # Fallback si no se puede hacer offset

        final_obj.Layer = LAYER_DEBUG
        final_obj.Color = color
    except Exception as e:
        logger.debug(f"Error al dibujar ruta debug: {e}")


def dibujar_circulo_error(
    msp: Any,
    punto: Tuple[float, float],
    radio: Optional[float] = None,
    capa: str = "ERRORES_TOPOLOGIA",
) -> None:
    """
    Dibuja un círculo rojo en el plano para marcar una inconsistencia topológica.

    Args:
        msp (Any): ModelSpace.
        punto (Tuple[float, float]): Coordenada (x, y) del error.
        radio (Optional[float]): Radio del círculo. Si es None, lee de config.
        capa (str): Nombre de la capa donde dibujar.
    """
    if radio is None:
        radio = RADIO_ERROR
    try:
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (punto[0], punto[1], 0)
        )
        circulo = msp.AddCircle(center, radio)
        circulo.Color = COLOR_ERROR
        circulo.Layer = capa
    except Exception:
        pass


def dibujar_grafo_completo(
    msp: Any,
    grafo: Any,
    capa_nodos: str = "DEBUG_GRAFO_NODOS",
    capa_aristas: str = "DEBUG_GRAFO_ARISTAS",
) -> None:
    """
    Dibuja la representación visual completa del grafo de red vial.
    AVISO: Puede ser lento en planos muy grandes.

    Args:
        msp (Any): ModelSpace.
        grafo (NetworkGraph): Instancia del grafo con nodos y adyacencias.
    """
    logger.info(" Dibujando grafo completo (esto puede tardar)...")

    dibujados = set()
    # Dibujar aristas
    for nodo_id, vecinos in grafo.adj.items():
        p1 = grafo.nodes[nodo_id]
        for vecino_id, _ in vecinos:
            # Ordenar IDs para evitar dibujar A->B y B->A (duplicado)
            edge_key = tuple(sorted((nodo_id, vecino_id)))
            if edge_key in dibujados:
                continue  # Ya dibujado

            p2 = grafo.nodes[vecino_id]

            start = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8, (p1[0], p1[1], 0)
            )
            end = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8, (p2[0], p2[1], 0)
            )
            linea = msp.AddLine(start, end)
            linea.Layer = capa_aristas
            linea.Color = COLOR_GRAFO
            dibujados.add(edge_key)

    # Dibujar nodos
    for coords in grafo.nodes.values():
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (coords[0], coords[1], 0)
        )
        circulo = msp.AddCircle(center, RADIO_NODO)
        circulo.Layer = capa_nodos
        circulo.Color = 4  # Cyan
