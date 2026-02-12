"""
Módulo de Dibujo (Drawer).
Contiene funciones puras para dibujar entidades de diagnóstico en AutoCAD.
No realiza cálculos de ruta, solo visualización.
"""

from typing import List, Tuple, Optional, Any
import win32com.client
import pythoncom
from .constants import ASI, SysLayers, Geometry
from .feedback_logger import logger


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
        color = ASI.MAGENTA

    # Aplanar lista de puntos para el formato que exige win32com
    vertices = []
    for p in puntos:
        vertices.extend([p[0], p[1]])

    try:
        var_pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, vertices)
        pline = msp.AddLightWeightPolyline(var_pt)

        # Intentar realizar offset geométrico
        try:
            objs = pline.Offset(Geometry.OFFSET_RUTAS)
            pline.Delete()
            final_obj = objs[0]
        except Exception:
            final_obj = pline  # Fallback si no se puede hacer offset

        final_obj.Layer = SysLayers.DEBUG_RUTAS
        final_obj.Color = color
    except Exception as e:
        logger.debug(f"Error al dibujar ruta debug: {e}")


def dibujar_circulo_error(
    msp: Any,
    punto: Tuple[float, float],
    radio: Optional[float] = None,
    capa: str = SysLayers.ERRORES,
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
        radio = Geometry.RADIO_ERROR
    try:
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (punto[0], punto[1], 0)
        )
        circulo = msp.AddCircle(center, radio)
        circulo.Color = ASI.ROJO
        circulo.Layer = capa
    except Exception:
        pass


def dibujar_grafo_completo(
    msp: Any,
    grafo: Any,
    capa_nodos: str = SysLayers.DEBUG_NODOS,
    capa_aristas: str = SysLayers.DEBUG_ARISTAS,
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
            linea.Color = ASI.CYAN
            dibujados.add(edge_key)

    # Dibujar nodos
    for coords in grafo.nodes.values():
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (coords[0], coords[1], 0)
        )
        circulo = msp.AddCircle(center, Geometry.RADIO_NODO)
        circulo.Layer = capa_nodos
        circulo.Color = ASI.CYAN
