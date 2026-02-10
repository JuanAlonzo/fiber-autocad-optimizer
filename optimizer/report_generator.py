"""
Módulo de Reportes.
Genera archivos CSV compatibles con Excel a partir de los datos procesados.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .feedback_logger import logger


def exportar_csv(
    datos: List[Dict[str, Any]], nombre_archivo: Optional[str] = None
) -> None:
    """
    Exporta una lista de diccionarios a un archivo CSV.

    Args:
        datos (List[Dict[str, Any]]): Lista de tramos procesados (diccionarios).
        nombre_archivo (Optional[str]): Ruta personalizada. Si es None, genera una automática en 'reportes/'.
    """
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
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(encabezados)

            for d in datos:
                writer.writerow(
                    [
                        d.get("handle", ""),
                        d.get("origen", ""),
                        d.get("destino", ""),
                        f"{d.get('longitud_real', 0):.2f}",
                        d.get("cable_asignado", ""),
                        d.get("tipo_tecnico", ""),
                        f"{d.get('reserva', 0):.2f}",
                        d.get("estado", ""),
                    ]
                )
        logger.info(f"Reporte exportado en: {nombre_archivo}")

    except Exception as e:
        logger.error(f"Error al exportar CSV: {e}")
