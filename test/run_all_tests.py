"""
Ejecutor de todos los tests del optimizador de fibra óptica
Ejecuta tests en orden lógico y genera reporte de resultados
"""
import sys

# Colores para terminal (compatible con Windows)
try:
    import colorama
    colorama.init()
    COLOR_OK = "\033[92m"
    COLOR_WARN = "\033[93m"
    COLOR_ERROR = "\033[91m"
    COLOR_INFO = "\033[94m"
    COLOR_RESET = "\033[0m"
except ImportError:
    COLOR_OK = COLOR_WARN = COLOR_ERROR = COLOR_INFO = COLOR_RESET = ""


def print_header(text):
    """Imprime un encabezado destacado"""
    print("\n" + "="*70)
    print(f"{COLOR_INFO}{text}{COLOR_RESET}")
    print("="*70)


def run_test(test_name, test_function):
    """
    Ejecuta un test y captura el resultado

    Returns:
        bool: True si el test pasó, False si falló
    """
    print_header(f"Ejecutando: {test_name}")

    try:
        test_function()
        print(f"\n{COLOR_OK}{test_name} - PASÓ{COLOR_RESET}")
        return True
    except AssertionError as e:
        print(f"\n{COLOR_ERROR}{test_name} - FALLÓ{COLOR_RESET}")
        print(f"{COLOR_ERROR}   Razón: {e}{COLOR_RESET}")
        return False
    except Exception as e:
        print(f"\n{COLOR_ERROR}{test_name} - ERROR INESPERADO{COLOR_RESET}")
        print(f"{COLOR_ERROR}   Error: {e}{COLOR_RESET}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests en secuencia"""
    print(f"{COLOR_INFO}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   SUITE DE TESTS - OPTIMIZADOR DE FIBRA ÓPTICA AUTOCAD        ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{COLOR_RESET}")

    resultados = []

    # TEST 1: Lógica de selección de cables (sin AutoCAD)
    print_header("TEST 1: LÓGICA DE SELECCIÓN DE CABLES")
    print("Este test NO requiere AutoCAD abierto")
    input("Presiona ENTER para continuar...")

    try:
        from test_cable_rules import (
            test_seleccionar_cable_xbox_hub,
            test_seleccionar_cable_hub_fat,
            test_seleccionar_cable_expansion,
            test_casos_limite
        )

        resultados.append(("Cable Rules - XBOX→HUB",
                          run_test("XBOX→HUB", test_seleccionar_cable_xbox_hub)))
        resultados.append(
            ("Cable Rules - HUB→FAT", run_test("HUB→FAT", test_seleccionar_cable_hub_fat)))
        resultados.append(("Cable Rules - Expansión",
                          run_test("Expansión", test_seleccionar_cable_expansion)))
        resultados.append(("Cable Rules - Casos Límite",
                          run_test("Casos Límite", test_casos_limite)))

    except ImportError as e:
        print(f"{COLOR_ERROR}Error al importar test_cable_rules: {e}{COLOR_RESET}")
        resultados.append(("Cable Rules", False))

    # TEST 2: Detección de tramos en AutoCAD
    print_header("TEST 2: DETECCIÓN DE TRAMOS")
    print("REQUIERE: AutoCAD abierto con polilíneas en capas con 'TRAZO'")
    respuesta = input("¿Continuar con tests de AutoCAD? (s/n): ").lower()

    if respuesta == 's':
        try:
            from test_autocad_tramos import (
                test_obtener_tramos,
                test_validar_integridad_objetos,
                test_deteccion_capas_personalizadas
            )

            resultados.append(
                ("Tramos - Detección", run_test("Detección de Tramos", test_obtener_tramos)))
            resultados.append(
                ("Tramos - Integridad", run_test("Integridad de Objetos", test_validar_integridad_objetos)))
            resultados.append(
                ("Tramos - Capas", run_test("Detección de Capas", test_deteccion_capas_personalizadas)))

        except ImportError as e:
            print(
                f"{COLOR_ERROR}Error al importar test_autocad_tramos: {e}{COLOR_RESET}")
            resultados.append(("AutoCAD Tramos", False))
    else:
        print(f"{COLOR_WARN}Tests de tramos omitidos{COLOR_RESET}")

    # TEST 3: Detección de bloques
    print_header("TEST 3: DETECCIÓN DE BLOQUES")
    print("REQUIERE: AutoCAD abierto con bloques X_BOX, HUB_BOX, FAT_INT")
    respuesta = input("¿Continuar con test de bloques? (s/n): ").lower()

    if respuesta == 's':
        try:
            from test_autocad_bloques import test_deteccion_bloques

            resultados.append(
                ("Bloques - Detección", run_test("Detección de Bloques", test_deteccion_bloques)))

        except ImportError as e:
            print(
                f"{COLOR_ERROR}Error al importar test_autocad_bloques: {e}{COLOR_RESET}")
            resultados.append(("AutoCAD Bloques", False))
    else:
        print(f"{COLOR_WARN}Tests de bloques omitidos{COLOR_RESET}")

    # RESUMEN FINAL
    print_header("RESUMEN DE TESTS")

    total = len(resultados)
    pasados = sum(1 for _, resultado in resultados if resultado)
    fallados = total - pasados

    print(f"\nResultados:")
    for nombre, resultado in resultados:
        icono = f"{COLOR_OK}{COLOR_RESET}" if resultado else f"{COLOR_ERROR}{COLOR_RESET}"
        print(f"   {icono} {nombre}")

    print(f"\n{'='*70}")
    print(f"Total: {total} | {COLOR_OK}Pasados: {pasados}{COLOR_RESET} | {COLOR_ERROR}Fallados: {fallados}{COLOR_RESET}")
    print(f"{'='*70}")

    if fallados == 0:
        print(f"\n{COLOR_OK}¡TODOS LOS TESTS PASARON!{COLOR_RESET}")
        return 0
    else:
        print(
            f"\n{COLOR_WARN}Algunos tests fallaron. Revisa los errores arriba.{COLOR_RESET}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(
            f"\n\n{COLOR_WARN}Tests interrumpidos por el usuario{COLOR_RESET}")
        sys.exit(1)
