"""
Módulo de Topología: Identifica qué conecta cada tramo en el espacio.
"""

import math
from .config_loader import get_config


def obtener_puntos_extremos(poly_obj):
    """
    Obtiene las coordenadas (x,y) de inicio y fin de una polilínea.
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


def encontrar_bloque_cercano(punto, bloques, radio_max):
    """Busca el bloque más cercano (Snap a Equipos)."""
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


def calcular_ruta_completa(p_inicio, p_fin, grafo, lista_bloques):
    """
    Calcula la ruta completa (lista de puntos) entre dos coordenadas.
    Retorna: (distancia_total, lista_puntos_para_dibujar, metadata)
    """
    R_RADIUS = get_config("tolerancias.radio_busqueda_acceso", 20.0)
    UMB_DESPRECIO = get_config("tolerancias.desprecio_poste", 3.0)
    R_SNAP = get_config("tolerancias.radio_snap_equipos", 5.0)

    # Identifica Equipos (Inicio y Fin)
    eq_inicio, d_ini = encontrar_bloque_cercano(p_inicio, lista_bloques, R_SNAP)
    eq_fin, d_fin = encontrar_bloque_cercano(p_fin, lista_bloques, R_SNAP)

    if not eq_inicio or not eq_fin:
        return None, [], "Error: Extremo sin equipo cercano (<2m)"

    # Conectar a la Red (Grafo)
    # Buscamos el nodo de calle más cercano a cada equipo
    pos_ini = (eq_inicio["xyz"][0], eq_inicio["xyz"][1])
    pos_fin = (eq_fin["xyz"][0], eq_fin["xyz"][1])

    node_a, dist_acceso_a = grafo.find_nearest_node(pos_ini, max_radius=R_RADIUS)
    node_b, dist_acceso_b = grafo.find_nearest_node(pos_fin, max_radius=R_RADIUS)

    if not node_a or not node_b:
        return (
            None,
            [],
            f"Error: Equipo {eq_inicio['name']} o {eq_fin['name']} aislado de la calle",
        )

    # Calcular ruta en la calle
    dist_acceso_a_neta = dist_acceso_a if dist_acceso_a > UMB_DESPRECIO else 0.00
    dist_acceso_b_neta = dist_acceso_b if dist_acceso_b > UMB_DESPRECIO else 0.00

    dist_red, path_red = grafo.get_path_length(node_a, node_b)

    if dist_red is None:
        return None, [], "Error: Islas"

    # Construir resultado
    dist_total = dist_acceso_a_neta + dist_red + dist_acceso_b_neta

    # Armar visualización:
    # Equipo A -> Calle A -> ...Ruta... -> Calle B -> Equipo B
    camino_visual = [pos_ini] + path_red + [pos_fin]

    meta = {
        "origen": eq_inicio["name"],
        "destino": eq_fin["name"],
        "tipo_conexion": f"{eq_inicio['name']}->{eq_fin['name']}",  # Simplificado para demo
    }

    return dist_total, camino_visual, meta
