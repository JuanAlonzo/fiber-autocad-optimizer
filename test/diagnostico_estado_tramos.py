"""
Script de diagnóstico: Verifica el estado de los tramos antes de cambiar capas
"""
from pyautocad import Autocad
from optimizer import obtener_tramos, log_info, log_warning

acad = Autocad(create_if_not_exists=True)


def diagnosticar_estado_tramos():
    """
    Diagnostica el estado de todos los tramos y su capacidad de cambio de capa.
    """
    print("\n" + "="*70)
    print("  DIAGNÓSTICO DE ESTADO DE TRAMOS")
    print("="*70)

    tramos = obtener_tramos()

    if not tramos:
        log_warning("No se encontraron tramos")
        return

    log_info(f"Se encontraron {len(tramos)} tramo(s)\n")

    # Contadores
    puede_cambiar_capa = 0
    no_puede_cambiar_capa = 0
    puede_leer_boundingbox = 0
    no_puede_leer_boundingbox = 0
    esta_bloqueado = 0

    print(f"{'#':<4} {'Handle':<8} {'Longitud':<10} {'Capa':<12} {'BBox':<6} {'Lock':<6} {'Estado'}")
    print("-" * 70)

    for i, tramo in enumerate(tramos, 1):
        handle = tramo["handle"]
        longitud = tramo["longitud"]
        capa_original = tramo["layer"]
        obj = tramo["obj"]

        # Test 1: Intentar cambiar capa (y restaurar)
        puede_cambiar = False
        try:
            capa_temp = obj.Layer
            obj.Layer = "TEST_TEMP_LAYER"
            obj.Layer = capa_temp  # Restaurar
            puede_cambiar = True
            puede_cambiar_capa += 1
        except:
            no_puede_cambiar_capa += 1

        # Test 2: Intentar leer BoundingBox
        puede_bbox = False
        try:
            pmin, pmax = obj.GetBoundingBox()
            puede_bbox = True
            puede_leer_boundingbox += 1
        except:
            no_puede_leer_boundingbox += 1

        # Test 3: Verificar si está bloqueado
        bloqueado = False
        try:
            bloqueado = obj.Locked
            if bloqueado:
                esta_bloqueado += 1
        except:
            bloqueado = "?"

        # Determinar estado general
        if puede_cambiar and puede_bbox:
            estado = "OK"
        elif puede_cambiar and not puede_bbox:
            estado = "Sin BBox"
        elif not puede_cambiar and puede_bbox:
            estado = "Capa bloq"
        else:
            estado = "Error"

        # Mostrar resultado
        capa_corta = capa_original[:12] if len(
            capa_original) > 12 else capa_original
        print(f"{i:<4} {handle:<8} {longitud:<10.1f} {capa_corta:<12} {'✓' if puede_bbox else '✗':<6} {'✓' if bloqueado else '✗':<6} {estado}")

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DEL DIAGNÓSTICO")
    print("="*70)
    print(f"  Total de tramos: {len(tramos)}")
    print(f"\n  Cambio de capa:")
    print(f"    Pueden cambiar capa: {puede_cambiar_capa}")
    print(f"    NO pueden cambiar capa: {no_puede_cambiar_capa}")
    print(f"\n  BoundingBox (para etiquetas):")
    print(f"    Pueden leer BoundingBox: {puede_leer_boundingbox}")
    print(f"    NO pueden leer BoundingBox: {no_puede_leer_boundingbox}")
    print(f"\n  Estado de bloqueo:")
    print(f"    Objetos bloqueados: {esta_bloqueado}")
    print("="*70)

    # Recomendaciones
    if no_puede_cambiar_capa > 0 or no_puede_leer_boundingbox > 0:
        print("\nRECOMENDACIONES:")
        if no_puede_cambiar_capa > 0:
            print("  • Desbloquea las capas en AutoCAD (LAYER → Unlock All)")
            print("  • Verifica que no haya XREF bloqueadas")
        if no_puede_leer_boundingbox > 0:
            print("  • Ejecuta AUDIT en AutoCAD para corregir objetos")
            print("  • Algunos objetos pueden estar corruptos")
        if esta_bloqueado > 0:
            print(
                f"  • {esta_bloqueado} objeto(s) están marcados como bloqueados")
    else:
        print("\nTODOS LOS TRAMOS ESTÁN EN BUEN ESTADO")
        print("   Puedes proceder con el cambio de capa sin problemas")

    print("="*70)


def diagnosticar_tramo_especifico(handle):
    """
    Diagnóstico detallado de un tramo específico por su handle.

    Args:
        handle: Handle del tramo a diagnosticar
    """
    print(f"\n{'='*70}")
    print(f"  DIAGNÓSTICO DETALLADO - TRAMO {handle}")
    print("="*70)

    tramos = obtener_tramos()
    tramo = None

    for t in tramos:
        if t["handle"] == handle:
            tramo = t
            break

    if not tramo:
        print(f"Tramo {handle} no encontrado")
        return

    obj = tramo["obj"]

    tests = [
        ("Layer (Leer)", lambda: obj.Layer),
        ("Length (Leer)", lambda: obj.Length),
        ("Handle (Leer)", lambda: obj.Handle),
        ("Locked (Leer)", lambda: obj.Locked),
        ("Color (Leer)", lambda: obj.Color),
        ("Linetype (Leer)", lambda: obj.Linetype),
        ("GetBoundingBox", lambda: obj.GetBoundingBox()),
        ("Layer (Cambiar)", lambda: cambiar_y_restaurar_capa(obj)),
    ]

    print(f"\n{'Prueba':<30} {'Estado':<10} {'Resultado'}")
    print("-" * 70)

    for nombre, test in tests:
        try:
            resultado = test()
            print(f"{nombre:<30} {'OK':<10} {str(resultado)[:30]}")
        except Exception as e:
            error_msg = str(e)[:30]
            print(f"{nombre:<30} {'ERROR':<10} {error_msg}")

    print("="*70)


def cambiar_y_restaurar_capa(obj):
    """Intenta cambiar la capa y restaurarla"""
    capa_original = obj.Layer
    obj.Layer = "TEST_TEMP"
    obj.Layer = capa_original
    return "OK"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Diagnóstico de tramo específico
        handle = sys.argv[1]
        diagnosticar_tramo_especifico(handle)
    else:
        # Diagnóstico general
        diagnosticar_estado_tramos()

    input("\nPresiona Enter para salir...")
