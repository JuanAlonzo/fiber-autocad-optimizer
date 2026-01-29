"""
Lógica de selección automática de cables
Determina el cable ideal basándose en la topología (Origen->Destino) y la longitud.
"""

from .config_loader import get_config


def buscar_regla_topologica(nombre_origen, nombre_destino):
    """
    Devuelve la reserva mínima configurada para un tipo de cable.
    """
    reglas = get_config("reglas_topologia", [])

    n_origen = nombre_origen.upper()
    n_destino = nombre_destino.upper()

    for regla in reglas:
        if regla["origen"] in n_origen and regla["destino"] in n_destino:
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

    nombre_tecnico = config_prod.get("nombre_tecnico", "UNK")
    disponibles = sorted(config_prod["longitudes"])
    reserva_minima = config_prod.get("reserva_minima", 10)

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
