"""
Optimizador de Fibra Óptica para AutoCAD - Punto de Entrada Principal
"""
from optimizer import acad, asignar_cables, exportar_csv, obtener_tramos


if __name__ == "__main__":
    print("=== OPTIMIZADOR DE CABLEADO FIBRA AUTOCAD ===")
    print("1️.- Desde XBOX → HUB BOX (preco 300m)")
    print("2️.- Desde HUB BOX → FATS (200 / 150 / 100)")
    print("3️.- FATS EXPANSIÓN (100 / 50)")
    opcion = input("Selecciona tipo de tramo (1, 2 o 3): ")

    if opcion == "1":
        tipo = "xbox_hub"
    elif opcion == "2":
        tipo = "hub_fat"
    elif opcion == "3":
        tipo = "expansion"
    else:
        print("Opción inválida.")
        exit()

    tramos = obtener_tramos()
    print(f"Tramos encontrados: {len(tramos)}")

    resultados = asignar_cables(tramos, tipo, acad)
    exportar_csv(resultados)

    print("\nProceso completado.")
