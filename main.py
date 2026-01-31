from optimizer import (
    extract_specific_blocks,
    NetworkGraph,
    get_acad_com,
    seleccionar_cable,
    dibujar_debug_offset,
    insertar_etiqueta_inteligente,
    dibujar_circulo_error,
    dibujar_grafo_completo,
    calcular_ruta_completa,
    get_config,
    exportar_csv,
    logger,
)


def main():
    logger.info("--- INICIANDO OPTIMIZADOR HÍBRIDO ---")

    acad = get_acad_com()
    if not acad:
        return
    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # YAML
    CAPA_RED = get_config("rutas.capa_red_vial")
    CAPA_TRAMO = get_config("rutas.capa_tramos_logicos")

    # Construir Grafo de 'LINEA DE RED'
    logger.info("[1/3] Leyendo LINEA DE RED...")
    TOL_GRAFO = get_config("tolerancias.snap_grafo_vial", 0.1)

    grafo = NetworkGraph(tolerance=TOL_GRAFO)

    if get_config("debug.mostrar_grafo_completo", False):
        try:
            doc.Layers.Add("DEBUG_GRAFO_NODOS")
            doc.Layers.Item("DEBUG_GRAFO_ARISTAS")
        except Exception:
            pass
        dibujar_grafo_completo(msp, grafo)

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

    logger.info(f" -> {count_lines} calles indexadas. {len(grafo.nodes)} nodos.")

    # Ingesta: Leer Equipos
    logger.info("[2/3] Indexando equipos...")
    dic_equipos = get_config("equipos", {})
    lista_todos_bloques = []
    for lista in dic_equipos.values():
        lista_todos_bloques.extend(lista)

    bloques = extract_specific_blocks(lista_todos_bloques)
    logger.info(f"-> {len(bloques)} equipos encontrados.")
    # Procesar TRAMOS (Interacción Usuario)
    logger.info("[3/3] Procesando capa 'TRAMO'...")

    # Crear capa debug si no existe
    try:
        doc.Layers.Add(get_config("rutas.capa_debug"))
    except Exception:
        pass

    count = 0

    for i in range(msp.Count):
        try:
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

                    logger.info(f"  ✓ {meta['origen']} -> {meta['destino']}")
                    logger.info(f"    [Diagnóstico] {meta['desglose']}")
                    logger.info(
                        f"   Real: {dist_real:.0f}m | Cable: {cable_m}m | Reserva: {reserva:.0f}m | Tec: {tipo_tec}"
                    )

                    # Dibujar ruta debug
                    dibujar_debug_offset(msp, ruta_visual, color=1)

                    # Etiquetar en dibujo
                    texto = (
                        f"{tipo_tec} {cable_m}m | L:{dist_real:.0f}m R:{reserva:.0f}m"
                    )
                    insertar_etiqueta_inteligente(msp, ruta_visual, texto)
                    logger.info(f"✓ Tramo OK: {cable_m}m")

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
                    if isinstance(meta, str):
                        msg_error = meta
                        origen_err = "?"
                        destino_err = "?"
                    else:
                        msg_error = meta.get("error", "Error desconocido")
                        origen_err = meta.get("origen", "?")
                        destino_err = meta.get("destino", "?")
                    logger.warning(f" X Error en tramo: {msg_error}")

                    try:
                        doc.Layers.Add("ERRORES_TOPOLOGIA").Color = 1
                    except Exception:
                        pass
                    dibujar_circulo_error(msp, p_start, radio=5)

                    # GUARDAR ERROR TAMBIÉN
                    datos_reporte.append(
                        {
                            "handle": obj.Handle,
                            "origen": origen_err,
                            "destino": destino_err,
                            "longitud_real": 0,
                            "cable_asignado": "N/A",
                            "tipo_tecnico": "ERROR",
                            "reserva": 0,
                            "estado": f"ERROR: {msg_error}",  # Guardar el mensaje de error
                        }
                    )

        except Exception:
            logger.exception(f"Error CRITICO procesando entidad: {i}")
            print(
                f"(!) Error saltado en tramo índice {i}. Revisa el log para detalles."
            )
            continue

    logger.info("\nExportando reporte CSV...")
    exportar_csv(datos_reporte)
    logger.info(f"\n--- PROCESO FINALIZADO: {count} tramos procesados ---")


if __name__ == "__main__":
    main()
