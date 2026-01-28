"""
Módulo de Topología: Identifica qué conecta cada tramo en el espacio.
"""

import math


def distancia_euclidiana(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


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


def encontrar_bloque_cercano(punto, bloques, radio_max=5.0):
    """
    Busca el bloque más cercano a un punto dado dentro de un radio máximo.
    """
    mejor_bloque = None
    mejor_dist = float("inf")

    for bloque in bloques:
        # Asumimos que bloque['position'] es (x, y, z) o (x, y)
        pos_bloque = bloque["position"]
        dist = distancia_euclidiana(punto, (pos_bloque[0], pos_bloque[1]))

        if dist < mejor_dist:
            mejor_dist = dist
            mejor_bloque = bloque

    if mejor_dist <= radio_max:
        return mejor_bloque
    return None


def detectar_regla_por_topologia(tramo_obj, lista_bloques):
    """
    Analiza un tramo y determina si es 'xbox_hub' o 'distribucion'
    basándose en los bloques que tiene en sus extremos.
    """
    p_inicio, p_fin = obtener_puntos_extremos(tramo_obj)

    if not p_inicio:
        return "distribucion"  # Ante la duda, regla estándar

    # Buscar bloques en las puntas (Radio de tolerancia 5m, ajustable)
    b_inicio = encontrar_bloque_cercano(p_inicio, lista_bloques, radio_max=5.0)
    b_fin = encontrar_bloque_cercano(p_fin, lista_bloques, radio_max=5.0)

    nombres_conectados = []
    if b_inicio:
        nombres_conectados.append(b_inicio["name"].upper())
    if b_fin:
        nombres_conectados.append(b_fin["name"].upper())

    # Lógica Binaria Simplificada
    tiene_xbox = any("X_BOX" in n for n in nombres_conectados)
    tiene_hbox = any("HBOX" in n for n in nombres_conectados)

    # REGLA MAESTRA 1: Si conecta un XBOX con un HBOX -> Es cable de 300m
    if tiene_xbox and tiene_hbox:
        return "xbox_hub"

    # REGLA MAESTRA 2: Cualquier otra cosa (HBOX-FAT, FAT-FAT) -> Distribución
    return "distribucion"
