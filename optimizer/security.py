import os
import sys
import socket
from datetime import datetime
from .feedback_logger import logger


DOMAINS_ALLOWED = [
    "HFC-01",
    "HFC-02",
    "HFC-03",
    "HFC-04",
    "HFC-05",
    "HFC-06",
    "HFC-07",
    "HFC-08",
    "HFC-09",
]

FECHA_EXPIRACION = datetime(2026, 12, 31)


def verificar_entorno() -> None:
    """
    Verifica si el entorno de ejecución es seguro y autorizado.
    Si falla, cierra el programa inmediatamente.
    """
    if datetime.now() > FECHA_EXPIRACION:
        msg = "NO DISPONIBLE.\nEsta versión del software ha caducado.\nPor favor contacte al administrador (Alonso) para renovar."
        logger.critical("Bloqueo de seguridad: Licencia expirada.")
        _bloquear_y_salir("Software Expirado", msg)

    dominio_actual = os.environ.get("USERDOMAIN", "").upper()
    pc_name = socket.gethostname().upper()

    logger.debug(f"Nombre del PC: {pc_name} | Dominio actual: {dominio_actual}")

    if dominio_actual not in DOMAINS_ALLOWED:
        if pc_name != "HFC-01":
            msg = (
                f"⛔ ACCESO DENEGADO.\n\n"
                f"Este software tiene licencia exclusiva para uso dentro de la red corporativa.\n"
                f"Dominio detectado: {dominio_actual}\n"
                f"Equipo: {pc_name}"
            )
            logger.critical(
                f"Bloqueo de seguridad: Dominio no autorizado ({dominio_actual})."
            )
            _bloquear_y_salir("Acceso Denegado", msg)

    logger.info("Entorno verificado: Dominio autorizado.")


def _bloquear_y_salir(titulo: str, mensaje: str) -> None:
    """
    Mensaje de error crítico y salida inmediata.
    """
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal
        messagebox.showerror(titulo, mensaje)
        root.destroy()
    except Exception:
        print(f"\n{'=' * 20}\n{titulo.upper()}\n{mensaje}\n{'=' * 20}\n")
    sys.exit(1)
