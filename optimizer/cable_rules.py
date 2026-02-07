"""
Lógica de selección automática de cables
Determina el cable ideal basándose en la topología (Origen->Destino) y la longitud.
"""

from .config_loader import get_config


def obtener_grupo_equipo(nombre_bloque):
    """
    Busca a qué grupo pertenece un bloque (ej. 'FAT_INT_3.0_P' -> 'fat_int').
    """
    config_equipos = get_config("equipos", {})
    nombre_bloque = nombre_bloque.upper()

    for grupo, lista_nombres in config_equipos.items():
        # Convertimos la lista de config a mayúsculas para comparar seguro
        if any(nombre_bloque == n.upper() for n in lista_nombres):
            return grupo

    return "desconocido"


def buscar_regla_topologica(nombre_origen, nombre_destino):
    """
    Devuelve la reserva mínima configurada para un tipo de cable.
    """
    grupo_origen = obtener_grupo_equipo(nombre_origen)
    grupo_destino = obtener_grupo_equipo(nombre_destino)

    reglas = get_config("reglas_topologia", [])

    for regla in reglas:
        if (
            regla.get("origen_grupo") == grupo_origen
            and regla.get("destino_grupo") == grupo_destino
        ):
            return regla["id_catalogo"]

    return None


def seleccionar_cable(longitud, nombre_origen, nombre_destino):
    """
    Identifica el tipo de cable según la regla topológica.
    Busca el tamaño adecuado en el catálogo.
    """
    id_producto = buscar_regla_topologica(nombre_origen, nombre_destino)

    if not id_producto:
        id_producto = "distribucion_std"  # Valor por defecto

    config_prod = get_config(f"catalogo_cables.{id_producto}")

    if not config_prod:
        raise ValueError(f"Configuracion de cable '{id_producto}' no encontrado.")

    nombre_tecnico = config_prod.get("nombre_tecnico", "UNKNOWN_CABLE")
    disponibles = sorted(config_prod["longitudes"])
    reserva_minima = config_prod.get("reserva_minima", 15)

    # Seleccion matematica
    cable_seleccionado = None
    reserva_calculada = 0

    for cable in disponibles:
        reserva = cable - longitud
        if reserva >= reserva_minima:
            cable_seleccionado = cable
            reserva_calculada = reserva
            break

    if cable_seleccionado is None:
        cable_seleccionado = disponibles[-1]
        reserva_calculada = cable_seleccionado - longitud

    # Si ninguna cumple la reserva mínima, usar el mayor
    return cable_seleccionado, reserva_calculada, nombre_tecnico
