"""
Genera reportes en formato CSV
"""

import csv


def exportar_csv(resultados, archivo="logs/reporte_cables.csv"):
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Handle", "Capa", "Longitud", "Reserva", "Cable", "Capa_Cambiada", "Etiqueta_Creada"])
        for r in resultados:
            writer.writerow([
                r["handle"], 
                r["capa"], 
                round(r["longitud"], 2), 
                round(r["reserva"], 2),
                r["cable"],
                "Sí" if r.get("capa_cambiada", True) else "No",
                "Sí" if r.get("etiqueta_creada", True) else "No"
            ])
    print(f"Reporte exportado: {archivo}")
