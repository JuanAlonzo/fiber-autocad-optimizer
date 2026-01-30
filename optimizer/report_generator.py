"""
Genera reportes en formato CSV
"""

import csv
import os
from datetime import datetime
from .feedback_logger import logger


def exportar_csv(datos, nombre_archivo=None):
    if not datos:
        logger.warning("No hay datos para exportar.")
        return

    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reportes/reporte_tramos_{timestamp}.csv"

    try:
        os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)
    except Exception as e:
        logger.error(f"Error al crear directorio: {e}")
        return

    encabezados = [
        "handle",
        "origen",
        "destino",
        "longitud_real",
        "cable_asignado",
        "tipo_tecnico",
        "reserva",
        "estado",
    ]

    try:
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(encabezados)

            for d in datos:
                writer.writerow(
                    [
                        d["handle"],
                        d["origen"],
                        d["destino"],
                        f"{d['longitud_real']:.2f}",
                        d["cable_asignado"],
                        d["tipo_tecnico"],
                        f"{d['reserva']:.2f}",
                        d["estado"],
                    ]
                )
        logger.info(f"Reporte exportado en: {nombre_archivo}")

    except Exception as e:
        logger.error(f"Error al exportar CSV: {e}")
        return
