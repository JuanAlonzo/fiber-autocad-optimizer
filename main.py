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
    verificar_entorno,
    logger,
)


def main():
    # Seguridad: Verificacion de entorno de ejecucion
    verificar_entorno()
    logger.info("--- INICIANDO OPTIMIZADOR HÍBRIDO ---")

    acad = get_acad_com()
    if not acad:
        logger.critical("No se pudo conectar con AutoCAD.")
        return

    doc = acad.ActiveDocument
    msp = doc.ModelSpace
    logger.info(f"Plano abierto: {doc.Name}")

    # YAML
    CAPA_RED = get_config("rutas.capa_red_vial")
    CAPA_TRAMO = get_config("rutas.capa_tramos_logicos")
    TOL_GRAFO = get_config("tolerancias.snap_grafo_vial", 0.1)

    # Construir Grafo de la linea de red existente
    logger.info("[1/3] Digitalizando Linea de Red...")
    grafo = NetworkGraph(tolerance=TOL_GRAFO)

    if get_config("general.mostrar_grafo_completo", False):
        dibujar_grafo_completo(msp, grafo)

    count_lines = 0
    # Barrido eficiente de líneas de red
    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == CAPA_RED:
                p1 = obj.StartPoint
                p2 = obj.EndPoint
                grafo.add_line(
                    (p1[0], p1[1]), (p2[0], p2[1])
                )  # Hacer configurable dibujar la linea
                count_lines += 1
        except Exception:
            continue

    logger.info(f" -> {count_lines} calles indexadas. {len(grafo.nodes)} nodos.")

    # Indexar Equipos (Bloques)
    logger.info("[2/3] Indexando equipos...")
    dic_equipos = get_config("equipos", {})
    lista_todos_bloques = []
    for lista in dic_equipos.values():
        lista_todos_bloques.extend(lista)

    bloques = extract_specific_blocks(lista_todos_bloques)
    logger.info(f"-> {len(bloques)} equipos encontrados.")

    # Procesar TRAMOS (Interacción Usuario)
    logger.info("[3/3] Calculando rutas...")

    # Asegurar capa de debug
    capa_debug = get_config("rutas.capa_debug")
    try:
        doc.Layers.Add(capa_debug)
    except Exception:
        pass

    count_procesados = 0
    datos_reporte = []

    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            if not (
                obj.ObjectName == "AcDbPolyline" and obj.Layer.upper() == CAPA_TRAMO
            ):
                continue

            coords = obj.Coordinates
            if len(coords) < 4:
                continue  # Mal dibujada

            p_start = (coords[0], coords[1])
            p_end = (coords[-2], coords[-1])  # Último punto

            dist_real, ruta_visual, meta = calcular_ruta_completa(
                p_start, p_end, grafo, bloques
            )

            if dist_real:
                cable_m, reserva, tipo_tec = seleccionar_cable(
                    dist_real, meta["origen"], meta["destino"]
                )

                # Feedback al usuario
                count_procesados += 1
                logger.info(
                    f"  ✓ Tramo {count_procesados}: {meta['origen']} -> {meta['destino']}"
                )
                logger.debug(
                    f"    Detalle: Real={dist_real:.1f}m | Cable={cable_m}m | {tipo_tec}"
                )

                # Dibujar ruta debug
                dibujar_debug_offset(msp, ruta_visual, color=None)

                # Etiquetar en dibujo
                texto_etiqueta = (
                    f"{tipo_tec} {cable_m}m | L:{dist_real:.0f}m R:{reserva:.0f}m"
                )
                insertar_etiqueta_inteligente(msp, ruta_visual, texto_etiqueta)

                # GUARDAR DATO PARA CSV
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
                else:
                    msg_error = meta.get("error", "Error desconocido")

                logger.warning(f" X Error en tramo {obj.Handle}: {msg_error}")

                dibujar_circulo_error(msp, p_start)

                datos_reporte.append(
                    {
                        "handle": obj.Handle,
                        "origen": meta.get("origen", "?")
                        if isinstance(meta, dict)
                        else "?",
                        "destino": meta.get("destino", "?")
                        if isinstance(meta, dict)
                        else "?",
                        "longitud_real": 0,
                        "cable_asignado": "N/A",
                        "tipo_tecnico": "ERROR",
                        "reserva": 0,
                        "estado": f"ERROR: {msg_error}",
                    }
                )

        except Exception:
            logger.exception(f"Error CRITICO procesando entidad: {i}")
            continue

    # Generar reporte CSV
    logger.info("\nExportando reporte CSV...")
    exportar_csv(datos_reporte)
    logger.info(f"\n--- PROCESO FINALIZADO: {count_procesados} tramos procesados ---")


if __name__ == "__main__":
    main()
