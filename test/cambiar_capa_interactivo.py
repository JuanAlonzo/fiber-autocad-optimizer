"""
Script avanzado para cambiar capas de tramos con opciones interactivas
"""
from pyautocad import Autocad
from optimizer import obtener_tramos, log_info, log_warning, log_error

acad = Autocad()

# Catálogo de capas disponibles
CAPAS_DISPONIBLES = {
    "1": "CABLE PRECONECT 2H SM (150M)",
    "2": "CABLE PRECONECT 2H SM (200M)",
    "3": "CABLE PRECONECT 2H SM (300M)",
    "4": "CABLE PRECONECT 2H SM (100M)",
    "5": "CABLE PRECONECT 2H SM (50M)",
}


def mostrar_menu():
    """Muestra el menú de opciones de capas"""
    print("\n" + "="*60)
    print("  CAMBIO DE CAPA DE TRAMOS - SELECTOR INTERACTIVO")
    print("="*60)
    print("\nSelecciona la nueva capa:")
    for key, capa in CAPAS_DISPONIBLES.items():
        print(f"  {key}. {capa}")
    print("  0. CAPA PERSONALIZADA")
    print("="*60)


def obtener_capa_personalizada():
    """Permite al usuario ingresar una capa personalizada"""
    print("\nIngresa el nombre de la capa personalizada:")
    print("   Ejemplo: CABLE PRECONECT 2H SM (400M)")
    capa = input("   Nueva capa: ").strip()
    return capa


def confirmar_cambio(tramos, nueva_capa):
    """Solicita confirmación antes de realizar cambios"""
    print("\n" + "="*60)
    print(f"  CONFIRMACIÓN DE CAMBIOS")
    print("="*60)
    print(f"  Tramos encontrados: {len(tramos)}")
    print(f"  Nueva capa: {nueva_capa}")
    print("\n  Capas actuales a modificar:")

    # Mostrar capas únicas
    capas_unicas = set(t["layer"] for t in tramos)
    for capa in capas_unicas:
        count = sum(1 for t in tramos if t["layer"] == capa)
        print(f"    • {capa} ({count} tramo(s))")

    print("="*60)
    respuesta = input("\n¿Deseas continuar? (s/n): ").strip().lower()
    return respuesta in ['s', 'si', 'sí', 'y', 'yes']


def cambiar_capa_tramos_interactivo():
    """
    Cambia la capa de tramos de forma interactiva con confirmación.
    """
    # Obtener tramos
    print("\nBuscando tramos en AutoCAD...")
    tramos = obtener_tramos()

    if not tramos:
        log_warning("No se encontraron tramos con 'TRAMO' en el nombre de capa")
        input("\nPresiona Enter para salir...")
        return

    log_info(f" Se encontraron {len(tramos)} tramo(s)")

    # Mostrar menú y seleccionar capa
    mostrar_menu()
    opcion = input("\nSelecciona una opción: ").strip()

    if opcion == "0":
        nueva_capa = obtener_capa_personalizada()
        if not nueva_capa:
            log_error("Nombre de capa inválido")
            return
    elif opcion in CAPAS_DISPONIBLES:
        nueva_capa = CAPAS_DISPONIBLES[opcion]
    else:
        log_error("Opción inválida")
        return

    # Confirmar cambios
    if not confirmar_cambio(tramos, nueva_capa):
        print("\nOperación cancelada por el usuario")
        return

    # Realizar cambios
    print("\nCambiando capas...")
    print("="*60)

    exitosos = 0
    errores = 0
    detalles_errores = []

    for i, tramo in enumerate(tramos, 1):
        handle = tramo["handle"]
        capa_original = tramo["layer"]
        longitud = tramo["longitud"]
        obj = tramo["obj"]

        try:
            obj.Layer = nueva_capa
            exitosos += 1
            print(
                f" [{i}/{len(tramos)}] {handle} | {longitud:.1f}m | {capa_original[:30]}... → {nueva_capa[:30]}...")

        except Exception as e:
            errores += 1
            error_msg = str(e)

            if "Key not found" in error_msg or "-2145386476" in error_msg:
                msg = f" [{i}/{len(tramos)}] {handle} | Objeto bloqueado o corrupto"
                print(msg)
                detalles_errores.append(
                    {"handle": handle, "error": "Bloqueado/Corrupto"})
            else:
                msg = f" [{i}/{len(tramos)}] {handle} | {error_msg[:50]}"
                print(msg)
                detalles_errores.append({"handle": handle, "error": error_msg})

    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE LA OPERACIÓN")
    print("="*60)
    print(f"  Exitosos: {exitosos}")
    print(f"  Errores: {errores}")
    print(f"  Total: {len(tramos)}")

    if detalles_errores:
        print(f"\n  Tramos con errores:")
        for detalle in detalles_errores:
            print(f"    • {detalle['handle']}: {detalle['error'][:50]}")

    print("="*60)

    # Sugerencias
    if errores > 0:
        print("\nSUGERENCIAS:")
        print("  • Ejecuta AUDIT en AutoCAD para corregir objetos corruptos")
        print("  • Desbloquea todas las capas antes de ejecutar el script")
        print("  • Verifica que no haya referencias externas (XREF) bloqueadas")

    input("\nPresiona Enter para salir...")
    return exitosos, errores


def cambiar_capa_sin_confirmacion(nueva_capa):
    """
    Cambia la capa directamente sin interacción (para scripting).

    Args:
        nueva_capa: Nombre de la nueva capa a asignar

    Returns:
        tuple: (exitosos, errores)
    """
    tramos = obtener_tramos()

    if not tramos:
        return 0, 0

    exitosos = 0
    errores = 0

    for tramo in tramos:
        try:
            tramo["obj"].Layer = nueva_capa
            exitosos += 1
        except:
            errores += 1

    return exitosos, errores


if __name__ == "__main__":
    # Ejecutar en modo interactivo
    cambiar_capa_tramos_interactivo()
