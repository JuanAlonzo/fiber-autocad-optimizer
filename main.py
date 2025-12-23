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
    from optimizer import get_acad_instance, asignar_cables, exportar_csv, obtener_tramos, obtener_bloques, log_info, log_error, detectar_regla_por_topologia
except ImportError as e:
    print(f"\nError CRÍTICO de importación: {e}")
    sys.exit(1)


def procesar_automaticamente(acad):
    print("\n[1] Escaneando dibujo...")

    # 1. Obtener todos los bloques relevantes para la topología
    # Buscamos XBOX y HBOX que son los que definen la Regla 1
    # Los FATs no son estrictamente necesarios para diferenciar, ya que "si no es XBOX->HUB, es Distribución"
    print("    • Buscando bloques de referencia (X_BOX, HBOX)...")
    bloques = obtener_bloques(["X_BOX_P", "HBOX_3.5P"], acad)
    print(f"      -> Encontrados {len(bloques)} bloques clave.")

    # 2. Obtener tramos
    print("    • Buscando tramos de fibra...")
    tramos = obtener_tramos(acad)
    if not tramos:
        print("⚠️  No se encontraron tramos.")
        return
    print(f"      -> Encontrados {len(tramos)} tramos.")

    # 3. Clasificación y Asignación
    print("\n[2] Analizando topología y asignando cables...")
    print("    (Este proceso decide automáticamente si es MPO 300m o 2H Distr.)")

    confirmacion = input(
        "\n    ¿Deseas proceder con los cambios en AutoCAD? (s/n): ").lower()
    if confirmacion != 's':
        return

    # AQUI ESTÁ EL TRUCO:
    # En lugar de pasar un solo 'tipo' a asignar_cables,
    # vamos a iterar aquí y decidir tramo por tramo.

    resultados_totales = []

    # Agrupamos los tramos por su tipo detectado para enviarlos a asignar_cables por lotes
    # O mejor, modificamos asignar_cables para que acepte un solo tramo.
    # Pero para no reescribir todo logic_cable_assignment, hagamos grupos.

    grupo_xbox = []
    grupo_distribucion = []

    for tramo in tramos:
        # Magia de topología
        regla = detectar_regla_por_topologia(tramo['obj'], bloques)

        if regla == "xbox_hub":
            grupo_xbox.append(tramo)
        else:
            grupo_distribucion.append(tramo)

    print(f"\n    [Detección Finalizada]")
    print(f"    • Rutas Alimentación (XBOX-HUB): {len(grupo_xbox)}")
    print(f"    • Rutas Distribución (Resto):    {len(grupo_distribucion)}")

    # Procesar Grupo 1
    if grupo_xbox:
        log_info("\n--- Procesando Alimentación ---")
        res1 = asignar_cables(grupo_xbox, "xbox_hub", acad)
        resultados_totales.extend(res1)

    # Procesar Grupo 2
    if grupo_distribucion:
        log_info("\n--- Procesando Distribución ---")
        res2 = asignar_cables(grupo_distribucion, "distribucion", acad)
        resultados_totales.extend(res2)

    # 4. Reporte
    print(f"\n[3] Generando reporte unificado...")
    exportar_csv(resultados_totales)


def main():
    print("\n" + "="*50)
    print("   OPTIMIZADOR DE CABLEADO FIBRA AUTOCAD")
    print("="*50)

    # 1. Conexión a AutoCAD
    try:
        acad = get_acad_instance()
        print(f"    ✓ Conectado a: {acad.doc.Name}")

        procesar_automaticamente(acad)

    except Exception as e:
        print(f"\nError : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
