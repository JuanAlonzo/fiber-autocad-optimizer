"""
Cargador centralizado de configuración
"""

import yaml
import os
import sys
from .feedback_logger import logger

_config = None


def get_base_path():
    """Devuelve la ruta base del proyecto."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    """Calcula la ruta absoluta al config.yaml"""
    base_path = get_base_path()

    if getattr(sys, "frozen", False):
        return os.path.join(base_path, "config.yaml")
    else:
        return os.path.join(base_path, "..", "config.yaml")


def load_config():
    """Carga el YAML en memoria."""
    global _config
    ruta = get_config_path()

    try:
        with open(ruta, "r", encoding="utf-8") as file:
            _config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.critical(
            f"Error critico: No se encontro el archivo 'config.yaml' en: {ruta}."
        )
        _config = {}
    except Exception as e:
        logger.critical(f"Error critico al cargar la configuracion: {e}")
        _config = {}


def get_config(key_path, default=None):
    """
    Obtiene un valor de configuracion.
    """
    if _config is None:
        load_config()

    keys = key_path.split(".")
    value = _config
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default
