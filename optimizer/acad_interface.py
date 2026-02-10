"""
Módulo de interfaz con AutoCAD.
Gestiona la conexión COM con la aplicación activa.
"""

import win32com.client
from .feedback_logger import logger
from typing import Optional, Any


def get_acad_com() -> Optional[Any]:
    """
    Devuelve la instancia COM de AutoCAD activa mediante COM.
    Returns:
        Optional[Any]: Objeto 'AutoCAD.Application' si la conexión es exitosa,
                       None si falla o AutoCAD no está abierto.
    """
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        return acad
    except Exception as e:
        logger.critical(f"Error critico conectando con COM: {e}")
        return None
