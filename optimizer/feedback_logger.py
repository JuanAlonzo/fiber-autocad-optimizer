"""
Registra eventos y errores en un archivo de log
"""

from datetime import datetime
import logging
import os


def setup_logger():
    """Configura el logger global."""
    os.makedirs("logs", exist_ok=True)
    log_filename = f"logs/ejecucion_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger("FiberOptimizer")
    logger.setLevel(logging.DEBUG)  # Captura todo

    if logger.handlers:
        return logger

    # Handler de Archivo (Guarda TODO, incluso debug)
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_fmt)

    # Handler de Consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(message)s")  # Sin fecha en consola, más limpio
    console_handler.setFormatter(console_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Instancia global para importar
logger = setup_logger()
