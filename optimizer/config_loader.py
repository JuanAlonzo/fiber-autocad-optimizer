"""
Cargador centralizado de configuración
"""

import yaml
import os
import sys
from .feedback_logger import logger


def get_base_path():
    """Devuelve la ruta base del proyecto."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


if getattr(sys, "frozen", False):
    _current_dir = os.path.dirname(sys.executable)
else:
    _config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")


try:
    with open(_config_path, "r") as file:
        CONFIG = yaml.safe_load(file)
except FileNotFoundError:
    logger.critical(
        f"Error critico: No se encontro el archivo de configuracion 'config.yaml' en la ruta {_config_path}."
    )
    sys.exit(1)
except Exception as e:
    logger.critical(f"Error critico al cargar la configuracion: {e}")
    sys.exit(1)


def get_config(key_path, default=None):
    """
    Obtiene un valor de configuracion.
    """
    keys = key_path.split(".")
    value = CONFIG
    try:
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return default
