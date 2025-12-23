"""
Biblioteca de utilidades para comunicación con AutoCAD
"""

from pyautocad import Autocad
from .feedback_logger import log_warning
from .config_loader import get_config

_acad_instance = None


def get_acad_instance():
    """
    Devuelve la conexión activa o crea una nueva si no existe.
    Evita conectar al importar el archivo.
    """
    global _acad_instance
    if _acad_instance is None:
        _acad_instance = Autocad(create_if_not_exists=True)
    return _acad_instance


def obtener_bloques(nombres_bloques, acad=None):
    """
    Devuelve una lista de bloques en el dibujo con su nombre y capa.
    """
    if acad is None:
        acad = get_acad_instance()

    bloques = []
    for ent in acad.iter_objects("AcDbBlockReference"):
        try:
            if ent.Name in nombres_bloques:
                bloques.append({
                    "handle": ent.Handle,
                    "name": ent.Name,
                    "position": ent.InsertionPoint,
                    "layer": ent.Layer,
                    "obj": ent
                })
        except Exception:
            continue
    return bloques


def obtener_longitud_tramo(ent):
    """
    Devuelve la longitud si es una polilínea.
    """
    if ent.ObjectName == 'AcDbPolyline':
        return ent.Length
    return 0


def obtener_tramos(acad=None):
    """
    Devuelve una lista de polilíneas válidas con su longitud y capa.
    Maneja errores de acceso a propiedades de AutoCAD de forma robusta.
    """
    if acad is None:
        acad = get_acad_instance()

    filtro_capa = get_config(
        "general.filtro_capas_origen", "TRAMO").upper()

    tramos = []
    for ent in acad.iter_objects("AcDbPolyline"):
        try:
            # Intentar acceder a la capa primero (puede fallar)
            layer = ent.Layer

            # Solo procesar si contiene "TRAMO" en el nombre de capa
            if filtro_capa in layer.upper():
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
                    log_warning(
                        f"Error tramo {ent.Handle}: {e}")
                    continue
        except Exception as e:
            continue

    return tramos
