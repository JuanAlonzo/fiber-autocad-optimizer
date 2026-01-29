"""
Genera reportes en formato CSV
"""

import csv
import os
from .config_loader import get_config


def exportar_csv(datos, nombre_archivo=None):
    if not datos:
        print("No hay datos para exportar.")
        return

    if nombre_archivo is None:
        nombre_archivo = get_config(
            "general.ruta_reporte_csv", "logs/reporte_recorrido.csv"
        )

    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)

    encabezados = [
        "handle",
        "origen",
        "destino",
        "longitud_real",
        "cable_asignado",
        "tipo",
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
        print(f"Reporte exportado en: {nombre_archivo}")

    except Exception as e:
        print(f"Error al exportar CSV: {e}")
        return
