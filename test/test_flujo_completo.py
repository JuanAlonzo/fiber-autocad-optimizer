"""
Test integrado que simula el flujo completo del optimizador
sin modificar el dibujo de AutoCAD (modo dry-run)
"""
import sys

from optimizer import acad, log_info, log_warning, obtener_tramos, seleccionar_cable


def simular_asignacion_cables(tramos, tipo):
    """
    Simula la asignación de cables SIN modificar AutoCAD
    (útil para debugging y testing)
    """
    resultados = []

    print(f"\n{'='*70}")
    print(f"SIMULACIÓN DE ASIGNACIÓN - Tipo: {tipo.upper()}")
    print(f"{'='*70}\n")

    for i, tramo in enumerate(tramos, 1):
        long = tramo["longitud"]
        handle = tramo["handle"]

        # Determinar cable óptimo
        cable, reserva = seleccionar_cable(long, tipo)
        nueva_capa = f"CABLE PRECONNECT {tipo.upper()} SM ({cable}M)"

        # Validar reserva
        estado = "✓" if reserva >= 10 else "⚠️"

        print(f"{estado} Tramo #{i} (Handle: {handle})")
        print(f"   Longitud real: {long:.2f}m")
        print(f"   Cable asignado: {cable}m")
        print(f"   Reserva: {reserva:.2f}m")
        print(f"   Nueva capa: {nueva_capa}")

        if reserva < 10:
            print(f"   ADVERTENCIA: Reserva insuficiente (mínimo 10m)")
        if reserva < 0:
            print(f"   ERROR: Cable demasiado corto para este tramo!")

        print()

        resultados.append({
            "handle": handle,
            "longitud_real": long,
            "cable_asignado": cable,
            "reserva": reserva,
            "capa_destino": nueva_capa,
            "valido": reserva >= 10
        })

    return resultados


def generar_resumen(resultados, tipo):
    """Genera un resumen estadístico de la simulación"""
    print(f"\n{'='*70}")
    print(f"RESUMEN DE SIMULACIÓN - {tipo.upper()}")
    print(f"{'='*70}\n")

    total_tramos = len(resultados)
    tramos_validos = sum(1 for r in resultados if r["valido"])
    tramos_advertencia = sum(1 for r in resultados if 0 <= r["reserva"] < 10)
    tramos_error = sum(1 for r in resultados if r["reserva"] < 0)

    print(f"Estadísticas generales:")
    print(f"Total de tramos procesados: {total_tramos}")
    print(f"✓ Válidos (reserva >= 10m): {tramos_validos}")
    print(f"  Con advertencia (0-10m): {tramos_advertencia}")
    print(f"  Con error (reserva negativa): {tramos_error}")

    # Agrupar por tipo de cable
    cables_usados = {}
    for r in resultados:
        cable = r["cable_asignado"]
        if cable in cables_usados:
            cables_usados[cable] += 1
        else:
            cables_usados[cable] = 1

    print(f"\nCables utilizados:")
    for cable, cantidad in sorted(cables_usados.items()):
        print(f"   {cable}m: {cantidad} tramo(s)")

    # Estadísticas de longitudes
    longitudes = [r["longitud_real"] for r in resultados]
    reservas = [r["reserva"] for r in resultados]

    print(f"\nLongitudes de tramos:")
    print(f"   Mínima: {min(longitudes):.2f}m")
    print(f"   Máxima: {max(longitudes):.2f}m")
    print(f"   Promedio: {sum(longitudes)/len(longitudes):.2f}m")

    print(f"\nReservas:")
    print(f"   Mínima: {min(reservas):.2f}m")
    print(f"   Máxima: {max(reservas):.2f}m")
    print(f"   Promedio: {sum(reservas)/len(reservas):.2f}m")

    if tramos_advertencia > 0 or tramos_error > 0:
        print(f"\nRECOMENDACIONES:")
        if tramos_error > 0:
            print(
                f"   - Hay {tramos_error} tramo(s) que exceden el cable más largo disponible")
            print(f"   - Considera dividir estos tramos o usar cables más largos")
        if tramos_advertencia > 0:
            print(
                f"   - Hay {tramos_advertencia} tramo(s) con reserva insuficiente")
            print(f"   - Se usará el siguiente cable disponible automáticamente")


def test_flujo_completo():
    """Test del flujo completo sin modificar AutoCAD"""
    print("\n" + "="*70)
    print("TEST: FLUJO COMPLETO DE OPTIMIZACIÓN (DRY-RUN)")
    print("="*70)

    # Menú de tipos
    print("\nSelecciona el tipo de tramo a simular:")
    print("1. XBOX → HUB_BOX (MPO 12H 300m)")
    print("2. HUB_BOX → FATs (2H 200/150/100m)")
    print("3. FATs Expansión (1H 100/50m)")

    opcion = input("\nOpción (1/2/3): ").strip()

    tipo_map = {
        "1": "xbox_hub",
        "2": "hub_fat",
        "3": "expansion"
    }

    if opcion not in tipo_map:
        print("Opción inválida")
        return

    tipo = tipo_map[opcion]

    # Obtener tramos
    print(f"\n[1] Detectando tramos en AutoCAD...")
    tramos = obtener_tramos()

    if not tramos:
        print("No se encontraron tramos con 'TRAZO' en el nombre de capa")
        return

    print(f"✓ Encontrados: {len(tramos)} tramo(s)")

    # Simular asignación
    print(f"\n[2] Simulando asignación de cables tipo '{tipo}'...")
    resultados = simular_asignacion_cables(tramos, tipo)

    # Generar resumen
    print(f"\n[3] Generando resumen...")
    generar_resumen(resultados, tipo)

    print("\n" + "="*70)
    print("SIMULACIÓN COMPLETADA (No se modificó el dibujo)")
    print("="*70)


if __name__ == "__main__":
    try:
        test_flujo_completo()
    except KeyboardInterrupt:
        print("\n\n Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
