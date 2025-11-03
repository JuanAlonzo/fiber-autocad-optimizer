"""
Lógica de selección automática de cables
"""

import yaml
import os

# Obtener la ruta del archivo config.yaml desde la raíz del proyecto
_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', '..', 'config.yaml')

with open(_config_path, "r") as f:
    CONFIG = yaml.safe_load(f)

RESERVA_MINIMA = CONFIG["reserva_minima"]


def seleccionar_cable(longitud, tipo):
    """
    Determina el cable adecuado y su reserva.
    Si ninguna longitud cumple, devuelve el más largo disponible.
    """
    disponibles = sorted(CONFIG["capas_cables"][tipo]["longitudes"])
    for cable in disponibles:
        reserva = cable - longitud
        if reserva >= RESERVA_MINIMA:
            return cable, reserva
    # Si ninguna cumple la reserva mínima, usar el mayor
    return disponibles[-1], disponibles[-1] - longitud
