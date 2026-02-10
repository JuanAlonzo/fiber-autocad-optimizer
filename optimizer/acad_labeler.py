"""
Módulo de Etiquetado (Labeler).
Encargado de insertar textos inteligentes (Smart Labels) en el plano.
Maneja la rotación y posición automática basada en la geometría del tramo.
"""

from typing import Optional, Tuple, Any, List
import win32com.client
import pythoncom
from .config_loader import get_config
from .feedback_logger import logger
from .utils_math import (
    obtener_angulo_legible,
    obtener_punto_medio,
    obtener_vectores_offset,
)


def insertar_etiqueta_inteligente(
    msp: Any,
    ruta_puntos: List[Tuple[float, float]],
    texto: str,
    offset: Optional[float] = None,
) -> None:
    """
    Calcula la posición y rotación ideal para un texto y lo inserta en AutoCAD.
    El texto se alinea paralelo al segmento central de la polilínea.

    Args:
        msp (Any): ModelSpace.
        ruta_puntos (List[Tuple[float, float]]): Puntos que forman el tramo.
        texto (str): Contenido de la etiqueta.
        offset (Optional[float]): Distancia de separación perpendicular a la línea.
    """
    if len(ruta_puntos) < 2:
        return

    if offset is None:
        offset = get_config("etiquetas.offset_y", 0.5)

    # Tomar el segmento del medio
    idx = len(ruta_puntos) // 2
    p1 = ruta_puntos[idx]  # (x, y)
    # Intentamos tomar el siguiente punto, o el anterior si estamos al final
    p2 = ruta_puntos[idx + 1] if idx + 1 < len(ruta_puntos) else ruta_puntos[idx - 1]

    # Lógica vectorial para ángulo y offset
    mid_pt = obtener_punto_medio(p1, p2)
    vec_off = obtener_vectores_offset(p1, p2, offset)
    angulo = obtener_angulo_legible(p1, p2)

    # Coordenada Z explícita (0.0) requerida por AutoCAD
    pos_final = (mid_pt[0] + vec_off[0], mid_pt[1] + vec_off[1], 0.0)

    try:
        ins_pt = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, pos_final
        )
        txt_obj = msp.AddText(texto, ins_pt, get_config("etiquetas.altura_texto", 1.0))
        txt_obj.Rotation = angulo
        txt_obj.Alignment = get_config("etiquetas.alineacion", 13)
        txt_obj.TextAlignmentPoint = ins_pt
        txt_obj.Layer = get_config("etiquetas.capa_texto", "0")
        txt_obj.Color = get_config("visualizacion.color_ok", 3)  # Verde
    except Exception as e:
        logger.error(f"Error al insertar etiqueta: {e}")
