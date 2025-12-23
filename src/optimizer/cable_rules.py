"""
Lógica de selección automática de cables
"""
from .config_loader import CONFIG, get_config


def obtener_reserva_requerida(tipo):
    """
    Devuelve la reserva mínima configurada para un tipo de cable.
    """
    return get_config(f"capas_cables.{tipo}.reserva_minima", 10)


def seleccionar_cable(longitud, tipo):
    """
    Determina el cable adecuado y su reserva.
    """
    config_tipo = CONFIG["capas_cables"].get(tipo)

    if not config_tipo:
        raise ValueError(f"Tipo de cable desconocido: {tipo}")

    disponibles = sorted(config_tipo["longitudes"])
    reserva_minima = config_tipo.get("reserva_minima", 10)

    for cable in disponibles:
        reserva = cable - longitud
        if reserva >= reserva_minima:
            return cable, reserva
    # Si ninguna cumple la reserva mínima, usar el mayor
    return disponibles[-1], disponibles[-1] - longitud
