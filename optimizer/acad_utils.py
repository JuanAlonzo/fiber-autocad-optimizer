"""
Biblioteca de utilidades para comunicación con AutoCAD
"""

import math
from pyautocad import Autocad
from .config_loader import get_config
from .feedback_logger import log_warning

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


def obtener_centro_bbox(ent):
    """Calcula el punto central (x, y) del BoundingBox de una entidad."""
    try:
        pmin, pmax = ent.GetBoundingBox()
        cx = (pmin[0] + pmax[0]) / 2
        cy = (pmin[1] + pmax[1]) / 2
        return (cx, cy)
    except Exception:
        return None


def indexar_capa_referencia(acad, nombre_capa):
    """
    Escanea la capa real y guarda sus geometrías en memoria para búsqueda rápida.
    Retorna una lista de dicts: [{'centro': (x,y), 'longitud': 120.5}, ...]
    """
    referencias = []
    print(f"    • Indexando capa real '{nombre_capa}'...")

    # Optimizacion: Iteramos todo pero filtramos rápido por Layer
    # (pyautocad no permite filtrar iter_objects por capa nativamente sin iterar)
    count = 0
    for ent in acad.iter_objects("AcDbPolyline"):
        try:
            if ent.Layer.upper() == nombre_capa.upper():
                centro = obtener_centro_bbox(ent)
                if centro:
                    referencias.append(
                        {"centro": centro, "longitud": ent.Length, "handle": ent.Handle}
                    )
                    count += 1
        except Exception:
            continue

    print(f"      -> {count} rutas reales indexadas.")
    return referencias


def encontrar_longitud_real(centro_tramo, referencias, tolerancia):
    """
    Busca la línea de referencia más cercana al centro del tramo.
    """
    if not centro_tramo or not referencias:
        return None

    mejor_ref = None
    mejor_dist = float("inf")
    tx, ty = centro_tramo

    # Búsqueda lineal (para <5000 objetos es suficientemente rápido, <0.5s)
    for ref in referencias:
        rx, ry = ref["centro"]

        # Filtro rápido (Bounding Box check) para evitar raiz cuadrada costosa
        if abs(tx - rx) > tolerancia or abs(ty - ry) > tolerancia:
            continue

        # Distancia euclidiana real
        dist = math.sqrt((tx - rx) ** 2 + (ty - ry) ** 2)

        if dist < mejor_dist:
            mejor_dist = dist
            mejor_ref = ref

    if mejor_dist <= tolerancia:
        return mejor_ref["longitud"]
    return None


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
                bloques.append(
                    {
                        "handle": ent.Handle,
                        "name": ent.Name,
                        "position": ent.InsertionPoint,
                        "layer": ent.Layer,
                        "obj": ent,
                    }
                )
        except Exception:
            continue
    return bloques


def obtener_longitud_tramo(ent):
    """
    Devuelve la longitud si es una polilínea.
    """
    if ent.ObjectName == "AcDbPolyline":
        return ent.Length
    return 0


def obtener_tramos(acad=None):
    """
    Devuelve una lista de polilíneas válidas con su longitud y capa.
    Maneja errores de acceso a propiedades de AutoCAD de forma robusta.
    """
    if acad is None:
        acad = get_acad_instance()

    filtro_capa = get_config("general.filtro_capas_origen", "TRAMO").upper()
    # Configuración de referencia
    usar_ref = get_config("referencia_fisica.usar_referencia", False)
    capa_real = get_config("referencia_fisica.capa_real", "")
    tolerancia = get_config("referencia_fisica.tolerancia_busqueda", 10.0)

    referencias = []
    if usar_ref and capa_real:
        referencias = indexar_capa_referencia(acad, capa_real)

    tramos = []
    coincidencias = 0

    print(f"    • Escaneando tramos esquemáticos ('{filtro_capa}')...")

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
                    centro = obtener_centro_bbox(ent)

                    longitud_final = longitud
                    es_real = False

                    if referencias and centro:
                        long_real = encontrar_longitud_real(
                            centro, referencias, tolerancia
                        )
                        if long_real:
                            longitud_final = long_real
                            es_real = True
                            coincidencias += 1

                    tramos.append(
                        {
                            "handle": handle,
                            "layer": layer,
                            "longitud": longitud_final,
                            "longitud_dibujo": longitud,
                            "es_real": es_real,
                            "obj": ent,
                        }
                    )
                except Exception as e:
                    # Error al leer propiedades específicas
                    log_warning(f"Error tramo {ent.Handle}: {e}")
                    continue
        except Exception:
            continue
    if usar_ref:
        print(
            f"      -> {coincidencias}/{len(tramos)} tramos emparejados con ruta real."
        )
    return tramos
