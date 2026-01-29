from optimizer import (
    extract_specific_blocks,
    NetworkGraph,
    get_acad_com,
    seleccionar_cable,
    dibujar_debug_offset,
    insertar_etiqueta_inteligente,
    calcular_ruta_completa,
    get_config,
    exportar_csv,
)


def main():
    print("--- INICIANDO OPTIMIZADOR HÍBRIDO ---")

    acad = get_acad_com()
    if not acad:
        return
    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # YAML
    CAPA_RED = get_config("rutas.capa_red_vial")
    CAPA_TRAMO = get_config("rutas.capa_tramos_logicos")

    # Construir Grafo de 'LINEA DE RED'
    print("[1/3] Leyendo LINEA DE RED...")
    grafo = NetworkGraph(tolerance=0.1)

    count_lines = 0
    datos_reporte = []
    # Iteración optimizada para COM
    for i in range(msp.Count):
        obj = msp.Item(i)
        if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == CAPA_RED:
            p1 = obj.StartPoint
            p2 = obj.EndPoint
            grafo.add_line((p1[0], p1[1]), (p2[0], p2[1]))
            count_lines += 1

    print(f" -> {count_lines} calles indexadas. {len(grafo.nodes)} nodos.")

    # Ingesta: Leer Equipos
    print("[2/3] Indexando equipos...")
    bloques = extract_specific_blocks(
        ["X_BOX_P", "HBOX_3.5P", "FAT_INT_3.0_P", "FAT_FINAL_3.0_P"]
    )
    print(f"-> {len(bloques)} equipos encontrados.")

    # Procesar TRAMOS (Interacción Usuario)
    print("[3/3] Procesando capa 'TRAMO'...")

    # Crear capa debug si no existe
    try:
        doc.Layers.Add(get_config("rutas.capa_debug"))
    except Exception:
        pass

    count = 0
    for i in range(msp.Count):
        obj = msp.Item(i)
        if obj.ObjectName == "AcDbPolyline" and obj.Layer.upper() == CAPA_TRAMO:
            coords = obj.Coordinates
            if len(coords) < 4:
                continue  # Mal dibujada

            p_start = (coords[0], coords[1])
            p_end = (coords[-2], coords[-1])  # Último punto

            dist_real, ruta_visual, meta = calcular_ruta_completa(
                p_start, p_end, grafo, bloques
            )

            if dist_real:
                count += 1

                cable_m, reserva, tipo_tec = seleccionar_cable(
                    dist_real, meta["origen"], meta["destino"]
                )

                print(f"  ✓ {meta['origen']} -> {meta['destino']}")
                print(
                    f"   Real: {dist_real:.2f}m | Cable: {cable_m}m | Reserva: {reserva:.1f}m | Tec: {tipo_tec}"
                )

                # Dibujar ruta debug
                dibujar_debug_offset(msp, ruta_visual, color=1)

                # Etiquetar en dibujo
                texto = f"{tipo_tec} {cable_m}m | L:{dist_real:.1f}m R:{reserva:.1f}m"
                insertar_etiqueta_inteligente(msp, ruta_visual, texto)

                # GUARDAR DATO EN MEMORIA
                datos_reporte.append(
                    {
                        "handle": obj.Handle,
                        "origen": meta["origen"],
                        "destino": meta["destino"],
                        "longitud_real": dist_real,
                        "cable_asignado": cable_m,
                        "tipo_tecnico": tipo_tec,
                        "reserva": reserva,
                        "estado": "OK",
                    }
                )
            else:
                print(f" X Error en tramo {obj.Handle}: {meta}")
                # GUARDAR ERROR TAMBIÉN
                datos_reporte.append(
                    {
                        "handle": obj.Handle,
                        "origen": meta.get("origen", "?"),
                        "destino": meta.get("destino", "?"),
                        "longitud_real": 0,
                        "cable_asignado": "N/A",
                        "tipo_tecnico": "ERROR",
                        "reserva": 0,
                        "estado": f"ERROR: {meta}",  # Guardar el mensaje de error
                    }
                )

    print("\nExportando reporte CSV...")
    exportar_csv(datos_reporte)
    print(f"\n--- PROCESO FINALIZADO: {count} tramos procesados ---")


if __name__ == "__main__":
    main()
