"""
Módulo de Etiquetado (Labeler).
Encargado de insertar textos inteligentes (Smart Labels) en el plano.
Maneja la rotación y posición automática basada en la geometría del tramo.
"""

from typing import Optional, Tuple, Any, List
import win32com.client
import pythoncom
from .constants import ASI, Geometry, SysLayers
from .feedback_logger import logger
from .utils_math import (
    obtener_angulo_legible,
    obtener_punto_medio,
    obtener_vectores_offset,
)


def insertar_etiqueta_tramo(
    msp: Any,
    ruta_puntos: List[Tuple[float, float]],
    texto: str,
    offset: Optional[float] = None,
    capa: str = SysLayers.TEXTO_TRAMOS,
) -> None:
    """
    Inserta la etiqueta principal en el centro del tramo (Tipo y Longitud).
    Ejemplo: "2H SM 150m"
    """
    if len(ruta_puntos) < 2:
        return

    if offset is None:
        offset = 1.0  # Valor por defecto razonable si no se configura

    # 1. Calcular posición en el segmento central
    idx = len(ruta_puntos) // 2
    p1 = ruta_puntos[idx]
    # Intentar tomar el siguiente, o el anterior si es el último
    p2 = ruta_puntos[idx + 1] if idx + 1 < len(ruta_puntos) else ruta_puntos[idx - 1]

    mid_pt = obtener_punto_medio(p1, p2)
    vec_off = obtener_vectores_offset(p1, p2, offset)
    angulo = obtener_angulo_legible(p1, p2)

    # Posición final (X, Y, Z=0)
    pos_final = (mid_pt[0] + vec_off[0], mid_pt[1] + vec_off[1], 0.0)

    try:
        ins_pt = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, pos_final
        )

        # Crear texto
        txt_obj = msp.AddText(texto, ins_pt, Geometry.TEXT_HEIGHT)
        txt_obj.Rotation = angulo
        txt_obj.Alignment = Geometry.TEXT_ALIGNMENT_CENTER
        txt_obj.TextAlignmentPoint = ins_pt

        # Asignar propiedades
        txt_obj.Layer = capa
        txt_obj.Color = ASI.MAGENTA

    except Exception as e:
        logger.error(f"Error al etiquetar tramo: {e}")


def insertar_etiqueta_reserva(
    msp: Any,
    punto_destino: Tuple[float, float],
    reserva: float,
    capa: str = SysLayers.TEXTO_RESERVAS,
) -> None:
    """
    Inserta un texto pequeño con la reserva cerca del equipo destino.
    Ejemplo: "Reserva:15m"
    """
    if reserva <= 0:
        return

    texto = f"Reserva:{int(reserva)}m"

    # Offset fijo para que no caiga encima del bloque (ajustable)
    desplazamiento_x = 2.0
    desplazamiento_y = 2.0

    pos = (
        punto_destino[0] + desplazamiento_x,
        punto_destino[1] + desplazamiento_y,
        0.0,
    )

    try:
        ins_pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, pos)

        txt_obj = msp.AddText(texto, ins_pt, 0.8)
        txt_obj.Color = ASI.CYAN
        txt_obj.Layer = capa

    except Exception as e:
        logger.error(f"Error al etiquetar reserva: {e}")
