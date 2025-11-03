"""
Inserta etiquetas de texto en los tramos del dibujo en AutoCAD
"""

from pyautocad import APoint


def etiquetar_tramo(acad, obj, texto):
    """
    Inserta una etiqueta de texto encima del tramo.
    Maneja errores de acceso a objetos bloqueados o corruptos.
    """
    try:
        # Intentar obtener bounding box (puede fallar si el objeto está bloqueado)
        pmin, pmax = obj.GetBoundingBox()
        x = (pmin[0] + pmax[0]) / 2
        y = (pmin[1] + pmax[1]) / 2
        pos = APoint(x, y + 2)
        
        # Intentar crear el texto
        acad.model.AddText(texto, pos, 1.2)
    except Exception as e:
        # Re-lanzar la excepción para que sea manejada por el llamador
        raise Exception(f"Error al obtener bounding box o crear texto: {e}")
