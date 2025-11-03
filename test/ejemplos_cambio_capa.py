"""
Ejemplos de uso de los scripts de cambio de capa
"""

# =============================================================================
# EJEMPLO 1: Uso básico del script simple
# =============================================================================


def ejemplo_1_cambio_simple():
    """Cambiar todos los tramos a una capa fija"""
    from test.cambiar_capa import cambiar_capa_tramos

    # Cambiar a la capa predeterminada (150M)
    cambiar_capa_tramos()


# =============================================================================
# EJEMPLO 2: Cambio simple con capa personalizada
# =============================================================================

def ejemplo_2_capa_personalizada():
    """Cambiar todos los tramos a una capa específica"""
    from test.cambiar_capa import cambiar_capa_tramos

    # Cambiar a 300M
    cambiar_capa_tramos("CABLE PRECONECT 2H SM (300M)")


# =============================================================================
# EJEMPLO 3: Cambio programático sin confirmación
# =============================================================================

def ejemplo_3_sin_confirmacion():
    """Cambiar capa de forma programática (para scripts automáticos)"""
    from test.cambiar_capa_interactivo import cambiar_capa_sin_confirmacion

    # Cambiar directamente sin interacción
    exitosos, errores = cambiar_capa_sin_confirmacion(
        "CABLE PRECONECT 2H SM (200M)")

    print(f"Resultado: {exitosos} exitosos, {errores} errores")
    return exitosos, errores


# =============================================================================
# EJEMPLO 4: Cambio selectivo por longitud
# =============================================================================

def ejemplo_4_cambio_selectivo():
    """Cambiar capa solo de tramos que cumplen ciertas condiciones"""
    from optimizer import obtener_tramos, log_info

    tramos = obtener_tramos()

    for tramo in tramos:
        longitud = tramo["longitud"]
        obj = tramo["obj"]
        handle = tramo["handle"]

        try:
            # Asignar capa según longitud
            if longitud > 250:
                obj.Layer = "CABLE PRECONECT 2H SM (300M)"
                log_info(f" {handle}: {longitud:.1f}m → 300M")
            elif longitud > 180:
                obj.Layer = "CABLE PRECONECT 2H SM (200M)"
                log_info(f" {handle}: {longitud:.1f}m → 200M")
            else:
                obj.Layer = "CABLE PRECONECT 2H SM (150M)"
                log_info(f" {handle}: {longitud:.1f}m → 150M")
        except Exception as e:
            log_info(f" {handle}: Error - {e}")


# =============================================================================
# EJEMPLO 5: Diagnóstico antes de cambiar
# =============================================================================

def ejemplo_5_diagnostico_y_cambio():
    """Diagnosticar primero, luego cambiar solo los que están OK"""
    from optimizer import obtener_tramos, log_info, log_warning

    tramos = obtener_tramos()
    tramos_validos = []

    print("\nFASE 1: Diagnóstico")
    print("=" * 60)

    # Diagnosticar cada tramo
    for tramo in tramos:
        handle = tramo["handle"]
        obj = tramo["obj"]

        # Probar si se puede cambiar capa
        try:
            capa_temp = obj.Layer
            obj.Layer = "TEST_TEMP"
            obj.Layer = capa_temp  # Restaurar
            tramos_validos.append(tramo)
            print(f" {handle}: OK para cambio")
        except:
            log_warning(f" {handle}: No se puede modificar")

    print(f"\n Tramos válidos: {len(tramos_validos)}/{len(tramos)}")

    # Cambiar solo los válidos
    print("\n FASE 2: Cambio de capa")
    print("=" * 60)

    nueva_capa = "CABLE PRECONECT 2H SM (150M)"

    for tramo in tramos_validos:
        try:
            tramo["obj"].Layer = nueva_capa
            log_info(f" {tramo['handle']}: Cambiado a {nueva_capa}")
        except Exception as e:
            log_warning(f" {tramo['handle']}: Error inesperado - {e}")


# =============================================================================
# EJEMPLO 6: Cambio con backup de capa original
# =============================================================================

def ejemplo_6_con_backup():
    """Cambiar capa guardando un backup de las capas originales"""
    from optimizer import obtener_tramos, log_info
    import json

    tramos = obtener_tramos()
    backup = {}

    nueva_capa = "CABLE PRECONECT 2H SM (150M)"

    # Cambiar y guardar backup
    for tramo in tramos:
        handle = tramo["handle"]
        capa_original = tramo["layer"]
        obj = tramo["obj"]

        try:
            obj.Layer = nueva_capa
            backup[handle] = capa_original
            log_info(f" {handle}: {capa_original} → {nueva_capa}")
        except Exception as e:
            log_info(f" {handle}: Error - {e}")

    # Guardar backup en archivo
    with open("backup_capas.json", "w") as f:
        json.dump(backup, f, indent=2)

    print(f"\n Backup guardado en: backup_capas.json")
    print(f"  Tramos respaldados: {len(backup)}")


# =============================================================================
# EJEMPLO 7: Restaurar desde backup
# =============================================================================

def ejemplo_7_restaurar_backup():
    """Restaurar capas originales desde el backup"""
    from optimizer import log_info
    from pyautocad import Autocad
    import json

    acad = Autocad(create_if_not_exists=True)

    # Leer backup
    with open("backup_capas.json", "r") as f:
        backup = json.load(f)

    print(f"\n Restaurando {len(backup)} tramos...")

    restaurados = 0

    # Buscar cada tramo por handle y restaurar
    for ent in acad.iter_objects("AcDbPolyline"):
        try:
            handle = ent.Handle
            if handle in backup:
                capa_original = backup[handle]
                ent.Layer = capa_original
                restaurados += 1
                log_info(f" {handle}: Restaurado a {capa_original}")
        except:
            continue

    print(f"\n Restaurados: {restaurados}/{len(backup)}")


# =============================================================================
# EJEMPLO 8: Cambio por lotes (batch processing)
# =============================================================================

def ejemplo_8_batch_processing():
    """Procesar tramos en lotes para mejorar rendimiento"""
    from optimizer import obtener_tramos, log_info

    tramos = obtener_tramos()
    nueva_capa = "CABLE PRECONECT 2H SM (150M)"

    BATCH_SIZE = 5
    total_exitosos = 0

    # Procesar en lotes
    for i in range(0, len(tramos), BATCH_SIZE):
        batch = tramos[i:i+BATCH_SIZE]

        print(f"\n Procesando lote {i//BATCH_SIZE + 1} ({len(batch)} tramos)")

        for tramo in batch:
            try:
                tramo["obj"].Layer = nueva_capa
                total_exitosos += 1
                print(f"  {tramo['handle']}")
            except:
                print(f"  {tramo['handle']}")

        # Pequeña pausa entre lotes (opcional)
        import time
        time.sleep(0.1)

    print(f"\n Total procesados: {total_exitosos}/{len(tramos)}")


# =============================================================================
# EJEMPLO 9: Cambio con validación de nombre de capa
# =============================================================================

def ejemplo_9_validacion_capa():
    """Validar que la capa existe antes de cambiar"""
    from optimizer import obtener_tramos, log_info, log_warning, acad

    nueva_capa = "CABLE PRECONECT 2H SM (150M)"

    # Verificar si la capa existe
    capa_existe = False
    try:
        for layer in acad.doc.Layers:
            if layer.Name == nueva_capa:
                capa_existe = True
                break
    except:
        log_warning("No se pudo verificar capas existentes")

    # Crear capa si no existe
    if not capa_existe:
        print(f" La capa '{nueva_capa}' no existe")
        crear = input("¿Deseas crearla? (s/n): ").strip().lower()

        if crear in ['s', 'si', 'sí']:
            try:
                acad.doc.Layers.Add(nueva_capa)
                log_info(f" Capa '{nueva_capa}' creada")
            except Exception as e:
                log_warning(f" Error al crear capa: {e}")
                return
        else:
            print(" Operación cancelada")
            return

    # Cambiar tramos
    tramos = obtener_tramos()
    for tramo in tramos:
        try:
            tramo["obj"].Layer = nueva_capa
            log_info(f" {tramo['handle']}: Cambiado a {nueva_capa}")
        except Exception as e:
            log_warning(f" {tramo['handle']}: {e}")


# =============================================================================
# EJEMPLO 10: Reporte detallado en CSV
# =============================================================================

def ejemplo_10_reporte_csv():
    """Generar reporte CSV del cambio de capa"""
    from optimizer import obtener_tramos, log_info
    import csv
    from datetime import datetime

    tramos = obtener_tramos()
    nueva_capa = "CABLE PRECONECT 2H SM (150M)"

    resultados = []

    for tramo in tramos:
        handle = tramo["handle"]
        capa_original = tramo["layer"]
        longitud = tramo["longitud"]
        obj = tramo["obj"]

        try:
            obj.Layer = nueva_capa
            estado = "Exitoso"
            log_info(f" {handle}")
        except Exception as e:
            estado = f"Error: {str(e)[:30]}"
            log_info(f" {handle}")

        resultados.append({
            "Handle": handle,
            "Capa_Original": capa_original,
            "Nueva_Capa": nueva_capa,
            "Longitud": round(longitud, 2),
            "Estado": estado,
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Exportar a CSV
    archivo = "logs/cambio_capa_reporte.csv"
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
                                "Handle", "Capa_Original", "Nueva_Capa", "Longitud", "Estado", "Fecha"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\n Reporte exportado: {archivo}")


# =============================================================================
# MENÚ INTERACTIVO DE EJEMPLOS
# =============================================================================

def menu_ejemplos():
    """Muestra un menú para ejecutar los ejemplos"""
    ejemplos = {
        "1": ("Cambio simple (150M)", ejemplo_1_cambio_simple),
        "2": ("Cambio con capa personalizada (300M)", ejemplo_2_capa_personalizada),
        "3": ("Cambio sin confirmación", ejemplo_3_sin_confirmacion),
        "4": ("Cambio selectivo por longitud", ejemplo_4_cambio_selectivo),
        "5": ("Diagnóstico y cambio", ejemplo_5_diagnostico_y_cambio),
        "6": ("Cambio con backup", ejemplo_6_con_backup),
        "7": ("Restaurar desde backup", ejemplo_7_restaurar_backup),
        "8": ("Batch processing", ejemplo_8_batch_processing),
        "9": ("Validación de capa", ejemplo_9_validacion_capa),
        "10": ("Reporte CSV detallado", ejemplo_10_reporte_csv),
    }

    print("\n" + "="*70)
    print("  EJEMPLOS DE CAMBIO DE CAPA")
    print("="*70)

    for key, (nombre, _) in ejemplos.items():
        print(f"  {key}. {nombre}")

    print("  0. Salir")
    print("="*70)

    opcion = input("\nSelecciona un ejemplo: ").strip()

    if opcion in ejemplos:
        nombre, funcion = ejemplos[opcion]
        print(f"\n Ejecutando: {nombre}")
        print("="*70)
        funcion()
    elif opcion == "0":
        print(" ¡Hasta luego!")
    else:
        print(" Opción inválida")


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    menu_ejemplos()
