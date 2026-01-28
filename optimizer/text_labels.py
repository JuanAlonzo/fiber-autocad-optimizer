"""
Inserta etiquetas de texto en los tramos del dibujo en AutoCAD
"""

from pyautocad import APoint
from .config_loader import get_config


def etiquetar_tramo(acad, obj, texto):
    """
    Inserta una etiqueta de texto encima del tramo.
    Maneja errores de acceso a objetos bloqueados o corruptos.
    """

    offset_y = get_config("general.offset_y", 2)
    tamano_texto = get_config("general.tamano_texto", 1.2)

    try:
        # Intentar obtener bounding box (puede fallar si el objeto está bloqueado)
        pmin, pmax = obj.GetBoundingBox()
        x = (pmin[0] + pmax[0]) / 2
        y = (pmin[1] + pmax[1]) / 2
        pos = APoint(x, y + offset_y)

        # Intentar crear el texto
        acad.model.AddText(texto, pos, tamano_texto)
    except Exception as e:
        # Re-lanzar la excepción para que sea manejada por el llamador
        raise Exception(f"Error al etiquetar tramo: {e}")
