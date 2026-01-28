"""
Cargador centralizado de configuración
"""

import yaml
import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, "..", "config.yaml")


try:
    with open(_config_path, "r") as file:
        CONFIG = yaml.safe_load(file)
except FileNotFoundError:
    print(
        f"Error critico: No se encontro el archivo de configuracion 'config.yaml' en la ruta {_config_path}."
    )
    sys.exit(1)
except Exception as e:
    print(f"Error critico al cargar la configuracion: {e}")
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
