"""
Biblioteca de utilidades para comunicación con AutoCAD
"""

import win32com.client
import pythoncom
from .config_loader import get_config
from .feedback_logger import logger
from .utils_math import (
    obtener_angulo_legible,
    obtener_punto_medio,
    obtener_vectores_offset,
)


def get_acad_com():
    """
    Devuelve la instancia COM de AutoCAD activa.
    """
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        return acad
    except Exception as e:
        logger.critical(f"Error critico conectando con COM: {e}")
        return None


def dibujar_debug_offset(msp, puntos, color=None):
    """Dibuja polilínea con offset visual."""
    if not puntos or len(puntos) < 2:
        return

    distancia = get_config("rutas.offset_visual_debug", 0.5)
    layer = get_config("rutas.capa_debug", "DEBUG_RUTAS")

    if color is None:
        color = get_config("visualizacion.color_debug", 6)  # Magenta

    vertices = []
    for p in puntos:
        vertices.extend([p[0], p[1]])

    try:
        var_pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, vertices)
        pline = msp.AddLightWeightPolyline(var_pt)

        # Intentar offset
        try:
            objs = pline.Offset(distancia)
            pline.Delete()
            final_obj = objs[0]
        except Exception:
            final_obj = pline  # Fallback si no se puede hacer offset

        final_obj.Layer = layer
        final_obj.Color = color
    except Exception:
        pass


def insertar_etiqueta_inteligente(msp, ruta_puntos, texto, offset=None):
    """Calcula posición, rotación y pone el texto paralelo al tramo central."""
    if len(ruta_puntos) < 2:
        return

    if offset is None:
        offset = get_config("etiquetas.offset_y", 1.5)

    # Tomar el segmento del medio
    idx = len(ruta_puntos) // 2
    p1 = ruta_puntos[idx]  # (x, y)
    p2 = ruta_puntos[idx + 1]

    if p1 == p2 and idx + 2 < len(ruta_puntos):
        p2 = ruta_puntos[idx + 2]

    # Lógica vectorial para ángulo y offset
    mid_pt = obtener_punto_medio(p1, p2)
    vec_off = obtener_vectores_offset(p1, p2, offset)
    angulo = obtener_angulo_legible(p1, p2)

    pos_final = (mid_pt[0] + vec_off[0], mid_pt[1] + vec_off[1], 0.0)

    try:
        ins_pt = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, pos_final
        )
        txt_obj = msp.AddText(texto, ins_pt, 1.0)  # Altura 1.0
        txt_obj.Rotation = angulo
        txt_obj.Alignment = 13  # Bottom Center
        txt_obj.TextAlignmentPoint = ins_pt
        txt_obj.Layer = get_config("rutas.capa_debug", "0")
        txt_obj.Color = get_config("visualizacion.color_ok", 3)  # Verde
    except Exception as e:
        logger.error(f"Error al insertar etiqueta: {e}")


def dibujar_circulo_error(msp, punto, radio=None, capa="ERRORES_TOPOLOGIA"):
    """Dibuja un círculo rojo para marcar errores."""
    if radio is None:
        radio = 2.0
    try:
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (punto[0], punto[1], 0)
        )
        circulo = msp.AddCircle(center, radio)
        circulo.Color = get_config("visualizacion.color_error", 1)
        circulo.Layer = capa
    except Exception:
        pass


def dibujar_grafo_completo(
    msp, grafo, capa_nodos="DEBUG_GRAFO_NODOS", capa_aristas="DEBUG_GRAFO_ARISTAS"
):
    """Dibuja el grafo completo en AutoCAD para debug."""
    logger.info(" Dibujando grafo completo...")
    dibujados = set()
    for nodo_id, vecinos in grafo.adj.items():
        p1 = grafo.nodes[nodo_id]
        for vecino_id, _ in vecinos:
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
            linea.Color = 8  # Gris
            dibujados.add(edge_key)

    for coords in grafo.nodes.values():
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (coords[0], coords[1], 0)
        )
        pt = msp.AddPoint(center)
        pt.Layer = capa_nodos
        pt.Color = 4  # Cyan
