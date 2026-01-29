"""
Test unitario/integración para lectura de propiedades de bloques
"""

from optimizer import extract_specific_blocks


def test_extraccion_equipos():
    # Definir los objetivos
    bloques_objetivo = [
        "X_BOX_P",
        "HBOX_3.5P",
        "FAT_INT_3.0_P",
        "FAT_FINAL_3.0_P",
        "FAT_OUT_FIN_P",
    ]

    print(f"--- Iniciando búsqueda de: {', '.join(bloques_objetivo)} ---")

    # Ejecutar extracción
    resultados = extract_specific_blocks(bloques_objetivo)

    # Validaciones
    if not resultados:
        print("No se encontraron bloques. Asegúrate de tener el plano abierto.")
        return

    print(f"Se encontraron {len(resultados)} bloques en total.\n")

    # Reporte detallado por tipo
    conteo = {name: 0 for name in bloques_objetivo}

    for bloque in resultados:
        nombre = bloque["name"]
        if nombre in conteo:
            conteo[nombre] += 1

        print(f"Bloque: {nombre} (Handle: {bloque['handle']})")
        print(f"   Capa: {bloque['layer']}")
        print(f"   Pos: {bloque['xyz']}")

        if bloque["attributes"]:
            print("  Atributos encontrados:")
            for k, v in bloque["attributes"].items():
                print(f"      - {k}: {v}")
        else:
            print("   Sin atributos")
        if bloque["dynamic_props"]:
            # Solo mostramos algunas props interesantes para no saturar
            print("   Props Dinámicas (ejemplo):")
            keys = list(bloque["dynamic_props"].keys())[:3]
            for k in keys:
                print(f"      - {k}: {bloque['dynamic_props'][k]}")
        print("-" * 40)

    print("\n--- RESUMEN ---")
    for nombre, cantidad in conteo.items():
        estado = "✅" if cantidad > 0 else "⚠️"
        print(f"{estado} {nombre}: {cantidad} encontrados")


if __name__ == "__main__":
    test_extraccion_equipos()
