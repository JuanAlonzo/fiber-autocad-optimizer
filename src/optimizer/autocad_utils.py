"""
Biblioteca de utilidades para comunicación con AutoCAD
"""

from pyautocad import Autocad
from .feedback_logger import log_warning

acad = Autocad()


def obtener_bloques(nombres_bloques):
    """
    Devuelve una lista de bloques en el dibujo con su nombre y capa.
    """
    bloques = []
    for ent in acad.iter_objects:
        if ent.ObjectName == 'AcDbBlockReference':
            if ent.Name in nombres_bloques:
                bloques.append({
                    "handle": ent.Handle,
                    "name": ent.Name,
                    "position": ent.InsertionPoint,
                    "layer": ent.Layer,
                    "obj": ent
                })
    return bloques


def obtener_longitud_tramo(ent):
    # Funciona si el tramo es una polilínea
    if ent.ObjectName == 'AcDbPolyline':
        return ent.Length
    return 0


def obtener_tramos():
    """
    Devuelve una lista de polilíneas válidas con su longitud y capa.
    Maneja errores de acceso a propiedades de AutoCAD de forma robusta.
    """
    tramos = []
    for ent in acad.iter_objects("AcDbPolyline"):
        try:
            # Intentar acceder a la capa primero (puede fallar)
            layer = ent.Layer

            # Solo procesar si contiene "TRAMO" en el nombre de capa
            if "TRAMO" in layer.upper():
                try:
                    # Intentar obtener propiedades necesarias
                    handle = ent.Handle
                    longitud = ent.Length

                    tramos.append({
                        "handle": handle,
                        "layer": layer,
                        "longitud": longitud,
                        "obj": ent
                    })
                except Exception as e:
                    # Error al leer propiedades específicas
                    try:
                        log_warning(
                            f"Error al procesar tramo {ent.Handle}: {e}")
                    except:
                        log_warning(
                            f"Error al procesar un tramo (no se pudo obtener handle): {e}")
                    continue
        except Exception as e:
            # Error al acceder a la capa o el objeto está corrupto/bloqueado
            # Silenciar este error ya que puede ser un objeto temporal o inválido
            continue

    return tramos
