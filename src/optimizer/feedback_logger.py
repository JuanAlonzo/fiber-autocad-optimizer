"""
Registra eventos y errores en un archivo de log
"""

import datetime
import os


def log_event(msg, tipo="INFO"):
    os.makedirs("logs", exist_ok=True)
    with open("logs/registro.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] [{tipo}] {msg}\n")


def log_error(msg):
    print(f"{msg}")
    log_event(msg, "ERROR")


def log_warning(msg):
    print(f"{msg}")
    log_event(msg, "WARNING")


def log_info(msg):
    print(f"{msg}")
    log_event(msg, "INFO")
