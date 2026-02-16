"""
Módulo de Configuración.
Carga y gestiona el archivo YAML de configuración centralizada.
Soporta ejecución tanto como script (.py) como ejecutable congelado (.exe).
"""

import yaml
import os
import sys
from typing import Any, Optional
from .feedback_logger import logger

_config: Optional[dict] = None
_current_config_path: str = "Automatico"


def get_base_path() -> str:
    """
    Devuelve la ruta base del proyecto, adaptándose al entorno de ejecución.

    Returns:
        str: Ruta del directorio base.
             - En modo .exe: La carpeta donde está el ejecutable.
             - En modo .py: La carpeta 'optimizer'.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path() -> str:
    """
    Calcula la ruta absoluta al archivo config.yaml.

    Returns:
        str: Ruta completa al archivo de configuración.
    """
    base_path = get_base_path()

    if getattr(sys, "frozen", False):
        return os.path.join(base_path, "config.yaml")
    else:
        return os.path.join(base_path, "..", "config.yaml")


def load_config(specific_path: Optional[str] = None) -> bool:
    """
    Carga el contenido del archivo YAML en memoria (variable global _config).
    Si falla, inicializa una configuración vacía y loguea el error crítico.
    """
    global _config, _current_config_path

    ruta = specific_path if specific_path else get_config_path()
    _current_config_path = ruta

    try:
        with open(ruta, "r", encoding="utf-8") as file:
            _config = yaml.safe_load(file)
        logger.info(f"Configuracion cargada desde {ruta}.")
        return True
    except FileNotFoundError:
        logger.critical(f"No se encontró el archivo en: {ruta}.")
        _config = {}
        return False
    except Exception as e:
        logger.critical(f"Error al cargar la configuracion: {e}")
        _config = {}
        return False


def get_config(key_path: str, default: Any = None) -> Any:
    """
    Obtiene un valor de la configuración usando notación de puntos.

    Args:
        key_path (str): Clave jerárquica (ej. 'rutas.capa_red_vial').
        default (Any): Valor a devolver si la clave no existe o falla la carga.

    Returns:
        Any: El valor configurado o el default.
    """
    if _config is None:
        load_config()

    if not _config:
        return default

    keys = key_path.split(".")
    value = _config
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def validar_configuracion() -> list[str]:
    """
    Verifica que existan las claves críticas.
    Retorna una lista de errores encontrados. Si está vacía, todo OK.
    """
    errores = []

    # Lista de claves obligatorias
    claves_criticas = [
        "rutas.capa_red_vial",
        "rutas.capa_tramos_logicos",
        "equipos.xbox",
        "equipos.hbox",
        "equipos.fat_int",
        "equipos.fat_final",
        "capas_resultado.prefijo_capa",
        "catalogo_cables",
    ]

    for clave in claves_criticas:
        if get_config(clave) is None:
            errores.append(f"Falta la clave crítica: '{clave}'")

    # Validación extra: Verificar que existan longitudes en los cables
    cables = get_config("catalogo_cables", {})
    if not cables:
        errores.append("La sección 'catalogo_cables' está vacía o no existe.")

    return errores
