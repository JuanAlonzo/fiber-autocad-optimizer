"""
Módulo de Topología: Identifica qué conecta cada tramo en el espacio.
Realiza el 'match' entre coordenadas geométricas y entidades lógicas (equipos).
"""

import math
from typing import Tuple, List, Dict, Optional, Any, Union
from .config_loader import get_config
from .feedback_logger import logger

Point2D = Tuple[float, float]

R_RADIUS = get_config("tolerancias.radio_busqueda_acceso", 20.0)
R_SNAP = get_config("tolerancias.radio_snap_equipos", 5.0)


def obtener_puntos_extremos(
    poly_obj: Any,
) -> Tuple[Optional[Point2D], Optional[Point2D]]:
    """
    Obtiene las coordenadas (x,y) de inicio y fin de una polilínea COM de AutoCAD.

    Args:
        poly_obj (Any): Objeto COM 'AcDbPolyline'.

    Returns:
        Tuple[Optional[Point2D], Optional[Point2D]]:
            ((x_ini, y_ini), (x_fin, y_fin)) o (None, None) si falla.
    """
    try:
        # Coordinates devuelve una tupla plana (x1, y1, x2, y2, ...)
        coords = poly_obj.Coordinates
        if not coords or len(coords) < 4:
            return None, None

        # Puntos 2D
        inicio = (coords[0], coords[1])
        fin = (coords[-2], coords[-1])
        return inicio, fin
    except Exception:
        return None, None


def encontrar_bloque_cercano(
    punto: Point2D, bloques: List[Dict[str, Any]], radio_max: float
) -> Tuple[Optional[Dict[str, Any]], Optional[float]]:
    """
    Busca el bloque más cercano a un punto dado dentro de un radio máximo.

    Args:
        punto (Point2D): Coordenada (x, y) de referencia.
        bloques (List[Dict]): Lista de diccionarios de bloques (debe contener clave "xyz").
        radio_max (float): Distancia máxima permitida para el snap.

    Returns:
        Tuple[Optional[Dict], Optional[float]]:
            (Mejor Bloque, Distancia) o (None, None) si no encuentra nada.
    """
    mejor_bloque = None
    mejor_dist = float("inf")

    for bloque in bloques:
        bx, by = bloque["xyz"][0], bloque["xyz"][1]
        dist = math.hypot(punto[0] - bx, punto[1] - by)

        if dist < mejor_dist:
            mejor_dist = dist
            mejor_bloque = bloque

    if mejor_dist <= radio_max:
        return mejor_bloque, mejor_dist
    return None, None


def calcular_ruta_completa(
    p_inicio: Point2D, p_fin: Point2D, grafo: Any, lista_bloques: List[Dict[str, Any]]
) -> Tuple[Optional[float], List[Point2D], Union[Dict[str, Any], str]]:
    """
    Calcula la ruta completa entre dos puntos geográficos, pasando por la red vial.

    Flujo:
    1. Identifica equipos cercanos a p_inicio y p_fin (Snap).
    2. Busca acceso a la red vial (Grafo).
    3. Calcula ruta más corta (Dijkstra).

    Args:
        p_inicio (Point2D): Coordenada inicial de la polilínea.
        p_fin (Point2D): Coordenada final de la polilínea.
        grafo (NetworkGraph): Instancia del grafo de red vial.
        lista_bloques (List[Dict]): Inventario de equipos disponibles.

    Returns:
        Tuple:
            - distancia_total (float | None): Distancia en metros o None si falla.
            - camino_visual (List[Point2D]): Lista de puntos para dibujar la ruta debug.
            - metadata (Dict | str): Datos del tramo (origen, destino) o mensaje de error.
    """

    # Identifica Equipos (Inicio y Fin)
    eq_inicio, d_ini = encontrar_bloque_cercano(
        p_inicio, lista_bloques, radio_max=R_SNAP
    )
    eq_fin, d_fin = encontrar_bloque_cercano(p_fin, lista_bloques, radio_max=R_SNAP)

    if not eq_inicio or not eq_fin:
        txt_d_ini = f"{d_ini:.1f}m" if d_ini is not None else "N/A"
        txt_d_fin = f"{d_fin:.1f}m" if d_fin is not None else "N/A"
        logger.debug(
            f"Fallo snap equipos: Ini={eq_inicio['name'] if eq_inicio else 'None'} ({txt_d_ini}), Fin={eq_fin['name'] if eq_fin else 'None'} ({txt_d_fin})"
        )
        return None, [], f"Error: Extremo sin equipo cercano (<{R_SNAP}m)"

    # Conectar a la Red (Grafo)
    # Buscamos el nodo de calle más cercano a cada equipo
    pos_ini: Point2D = (eq_inicio["xyz"][0], eq_inicio["xyz"][1])
    pos_fin: Point2D = (eq_fin["xyz"][0], eq_fin["xyz"][1])

    node_a, dist_acceso_a = grafo.find_nearest_node(pos_ini, max_radius=R_RADIUS)
    node_b, dist_acceso_b = grafo.find_nearest_node(pos_fin, max_radius=R_RADIUS)

    if not node_a or not node_b:
        # Logs detallados para depuración
        d_a_str = f"{dist_acceso_a}" if dist_acceso_a is not None else "Fuera de Rango"
        d_b_str = f"{dist_acceso_b}" if dist_acceso_b is not None else "Fuera de Rango"
        logger.debug(
            f"Equipo aislado de calle: {eq_inicio['name']} (DistRed: {d_a_str}), {eq_fin['name']} (DistRed: {d_b_str})"
        )
        return (
            None,
            [],
            f"Error: Equipo aislado de la red (<{R_RADIUS}m)",
        )

    dist_red, path_red = grafo.get_path_length(node_a, node_b)

    if dist_red is None:
        logger.warning(
            f"ISLAS DETECTADAS: No hay camino entre nodos {node_a} y {node_b}"
        )
        return None, [], "Error: Islas (Red desconectada)"

    # Equipo A -> Punto A -> ...Ruta... -> Punto B -> Equipo B
    camino_visual = [pos_ini] + path_red + [pos_fin]

    d_acc_a = dist_acceso_a if dist_acceso_a else 0.00
    d_acc_b = dist_acceso_b if dist_acceso_b else 0.00

    meta = {
        "origen": eq_inicio["name"],
        "destino": eq_fin["name"],
        "tipo_conexion": f"{eq_inicio['name']}->{eq_fin['name']}",
        "desglose": f"Red: {dist_red:.2f}m (Accesos ignorados: {d_acc_a:.2f}m + {d_acc_b:.2f}m)",
    }

    return dist_red, camino_visual, meta
