"""
Biblioteca de utilidades para comunicación con AutoCAD
"""

import win32com.client
import pythoncom
import math
from .config_loader import get_config


def get_acad_com():
    """
    Devuelve la instancia COM de AutoCAD activa.
    """
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        return acad
    except Exception as e:
        print(f"Error critico conectando con COM: {e}")
        return None


def dibujar_debug_offset(msp, puntos, color=1):
    """Dibuja polilínea con offset visual."""
    distancia = get_config("rutas.offset_visual_debug", 0.5)
    layer = get_config("rutas.capa_debug", "DEBUG_RUTAS")

    if not puntos or len(puntos) < 2:
        return

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


def insertar_etiqueta_inteligente(msp, ruta_puntos, texto):
    """Calcula posición, rotación y pone el texto paralelo al tramo central."""
    if len(ruta_puntos) < 2:
        return

    # Tomar el segmento del medio
    idx = len(ruta_puntos) // 2
    p1 = ruta_puntos[idx]  # (x, y)
    p2 = ruta_puntos[idx + 1]  # (x, y) si existe, sino idx-1

    # Lógica vectorial para ángulo y offset
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angulo = math.atan2(dy, dx)

    # Corregir lectura (evitar texto de cabeza)
    if abs(angulo) > math.pi / 2:
        angulo += math.pi
        inv = -1
    else:
        inv = 1

    # Vector normal unitario (-dy, dx)
    L = math.hypot(dx, dy)
    if L == 0:
        return

    offset_dist = 1.5 * inv  # Distancia del texto a la línea
    ox = (-dy / L) * offset_dist
    oy = (dx / L) * offset_dist

    mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

    # Insertar
    ins_pt = win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8, (mid_x + ox, mid_y + oy, 0)
    )
    txt = msp.AddText(texto, ins_pt, 1.0)  # Altura 1.0
    txt.Rotation = angulo
    txt.Alignment = 13  # Bottom Center
    txt.TextAlignmentPoint = ins_pt
    txt.Layer = get_config("rutas.capa_debug", "0")
