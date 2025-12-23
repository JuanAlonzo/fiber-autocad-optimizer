"""
Optimizador de Fibra Óptica para AutoCAD - Punto de Entrada Principal
"""
import sys
import os

# --- CORRECCIÓN DE IMPORTACIONES (FIX) ---
# Agregamos la carpeta 'src' al path de Python para que encuentre el módulo 'optimizer'
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# -----------------------------------------

# Ahora sí podemos importar sin errores
try:
    from optimizer import get_acad_instance, asignar_cables, exportar_csv, obtener_tramos, log_info, log_error
except ImportError as e:
    print(f"\n❌ Error CRÍTICO de importación: {e}")
    print(f"Verifica que la carpeta 'src/optimizer' contenga un archivo '__init__.py'")
    sys.exit(1)


def main():
    print("\n" + "="*50)
    print("   OPTIMIZADOR DE CABLEADO FIBRA AUTOCAD")
    print("="*50)

    # 1. Conexión a AutoCAD
    print("\n[1] Conectando con AutoCAD...")
    try:
        acad = get_acad_instance()
        print(f"    ✓ Conectado a: {acad.doc.Name}")
    except Exception as e:
        print(f"\n❌ Error al conectar con AutoCAD: {e}")
        print("Asegúrate de tener un dibujo abierto.")
        return

    # 2. Menú de Selección
    print("\n[2] Configuración de Trabajo")
    print("    1. Desde XBOX → HUB BOX (MPO 12H - Reserva 15m)")
    print("    2. Desde HUB BOX → FATS (2H - Reserva 10m)")
    print("    3. FATS EXPANSIÓN (1H - Reserva 10m)")

    opcion = input("\n    👉 Selecciona tipo de tramo (1, 2 o 3): ").strip()

    if opcion == "1":
        tipo = "xbox_hub"
    elif opcion == "2":
        tipo = "hub_fat"
    elif opcion == "3":
        tipo = "expansion"
    else:
        print("\n❌ Opción inválida. Saliendo.")
        return

    # 3. Obtención de Tramos
    print(f"\n[3] Buscando tramos en el dibujo...")
    # Pasamos 'acad' para reusar la conexión
    tramos = obtener_tramos(acad)

    if not tramos:
        print("\n⚠️  No se encontraron tramos.")
        print("    Verifica que las capas contengan el texto configurado (ej. 'TRAMO').")
        print("    Revisa 'config.yaml' si necesitas cambiar el filtro.")
        return

    print(f"    ✓ Se encontraron {len(tramos)} tramo(s) válidos.")

    # 4. Procesamiento
    print(f"\n[4] Asignando cables y etiquetas ({tipo})...")
    confirmacion = input(
        "    ¿Deseas proceder con los cambios en AutoCAD? (s/n): ").lower()

    if confirmacion != 's':
        print("\nOperación cancelada por el usuario.")
        return

    # Ejecutar lógica principal
    resultados = asignar_cables(tramos, tipo, acad)

    # 5. Reporte
    print(f"\n[5] Generando reporte...")
    exportar_csv(resultados)

    print("\n" + "="*50)
    print("   PROCESO COMPLETADO CON ÉXITO")
    print("="*50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")
        import traceback
        traceback.print_exc()
