"""
Módulo de Logging (Feedback).
Configura el sistema de registro de eventos y errores.
Guarda un historial detallado en la carpeta 'logs/' y muestra resumen en consola.
"""

from datetime import datetime
import logging
import sys
import os


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
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_logger() -> logging.Logger:
    """
    Configura y devuelve la instancia global del logger.

    - FileHandler: Guarda TODO (DEBUG) en logs/ejecucion_YYYYMMDD.log con encoding utf-8.
    - StreamHandler: Muestra INFO o superior en la consola (sin fecha para limpieza).

    Returns:
        logging.Logger: Instancia configurada lista para usar.
    """
    base_path = get_base_path()

    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)

    filename = f"ejecucion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file_path = os.path.join(log_dir, filename)

    logger = logging.getLogger("FiberOptimizer")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # Handler de Archivo
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_fmt)

    # Handler de Consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
