"""
Test completo para autocad_utils.py
Valida la detección y lectura de tramos (polilíneas)
"""
import sys

from pyautocad import Autocad, APoint

from optimizer import log_info, obtener_longitud_tramo, obtener_tramos


def test_obtener_tramos():
    """Test de detección de tramos en AutoCAD"""
    print("\n" + "="*60)
    print("TEST: DETECCIÓN DE TRAMOS (POLILÍNEAS)")
    print("="*60)

    print("\n[1] Conectando con AutoCAD...")
    try:
        acad = Autocad(create_if_not_exists=True)
        print("✓ Conexión exitosa con AutoCAD")
    except Exception as e:
        print(f"Error al conectar con AutoCAD: {e}")
        print("Asegúrate de que AutoCAD esté abierto")
        return

    print("\n[2] Buscando tramos con 'TRAMO' en el nombre de capa...")
    tramos = obtener_tramos()

    if not tramos:
        print("NO SE ENCONTRARON TRAMOS")
        print("Verifica que existan polilíneas en capas que contengan 'TRAMO'")
        print("Ejemplos de capas válidas: TRAMO, TRAMO_PRINCIPAL, TRAMOS_CABLE, etc.")
        return

    print(f"\n✓ Total de tramos encontrados: {len(tramos)}")

    # Análisis detallado de los primeros 5 tramos
    print(f"\n[3] Detalles de los primeros {min(5, len(tramos))} tramos:")
    for i, tramo in enumerate(tramos[:5]):
        print(f"\nTramo #{i+1}:")
        print(f"Handle: {tramo['handle']}")
        print(f"Capa: {tramo['layer']}")
        print(f"Longitud: {tramo['longitud']:.2f} unidades")

        # Verificar que todas las propiedades estén presentes
        assert "handle" in tramo, "Falta propiedad 'handle'"
        assert "layer" in tramo, "Falta propiedad 'layer'"
        assert "longitud" in tramo, "Falta propiedad 'longitud'"
        assert "obj" in tramo, "Falta propiedad 'obj'"
        assert tramo["longitud"] > 0, "Longitud debe ser mayor a 0"

    # Estadísticas
    longitudes = [t["longitud"] for t in tramos]
    print(f"\n[4] Estadísticas de longitudes:")
    print(f"Mínima: {min(longitudes):.2f} unidades")
    print(f"Máxima: {max(longitudes):.2f} unidades")
    print(f"Promedio: {sum(longitudes)/len(longitudes):.2f} unidades")

    # Capas únicas
    capas_unicas = set(t["layer"] for t in tramos)
    print(f"\n[5] Capas encontradas ({len(capas_unicas)}):")
    for capa in sorted(capas_unicas):
        count = sum(1 for t in tramos if t["layer"] == capa)
        print(f" - {capa}: {count} tramo(s)")

    print("\n" + "="*60)
    print("TEST DE TRAMOS COMPLETADO")
    print("="*60)


def test_validar_integridad_objetos():
    """Valida que los objetos de AutoCAD sean accesibles"""
    print("\n" + "="*60)
    print("TEST: VALIDACIÓN DE INTEGRIDAD DE OBJETOS")
    print("="*60)

    tramos = obtener_tramos()

    if not tramos:
        print("No hay tramos para validar")
        return

    print(f"\n[1] Validando acceso a propiedades de {len(tramos)} tramos...")

    errores = 0
    exitosos = 0

    for i, tramo in enumerate(tramos):
        try:
            # Intentar acceder a propiedades críticas
            _ = tramo["obj"].Handle
            _ = tramo["obj"].Layer
            _ = tramo["obj"].Length
            _ = tramo["obj"].ObjectName

            exitosos += 1

            if i < 3:  # Mostrar detalles de los primeros 3
                print(
                    f"✓ Tramo {tramo['handle']}: Todas las propiedades accesibles")

        except Exception as e:
            errores += 1
            print(f"Tramo {tramo.get('handle', 'DESCONOCIDO')}: Error - {e}")

    print(f"\n[2] Resultados:")
    print(f"   ✓ Exitosos: {exitosos}/{len(tramos)}")
    print(f"   Con errores: {errores}/{len(tramos)}")

    if errores > 0:
        print(
            f"\n  ADVERTENCIA: {errores} objetos tienen problemas de acceso")
        print("   Esto puede deberse a:")
        print("   - Objetos bloqueados en el dibujo")
        print("   - Referencias externas (Xrefs)")
        print("   - Objetos en capas congeladas")

    print("\n" + "="*60)
    print("TEST DE INTEGRIDAD COMPLETADO")
    print("="*60)


def test_deteccion_capas_personalizadas():
    """Test para detectar todas las capas con polilíneas"""
    print("\n" + "="*60)
    print("TEST: DETECCIÓN DE TODAS LAS CAPAS CON POLILÍNEAS")
    print("="*60)

    try:
        acad = Autocad(create_if_not_exists=True)

        print("\n[1] Escaneando todas las polilíneas en el dibujo...")

        capas_dict = {}  # {nombre_capa: cantidad}

        for ent in acad.iter_objects("AcDbPolyline"):
            try:
                capa = ent.Layer
                if capa in capas_dict:
                    capas_dict[capa] += 1
                else:
                    capas_dict[capa] = 1
            except:
                continue

        print(f"\n[2] Capas encontradas ({len(capas_dict)}):")
        for capa, cantidad in sorted(capas_dict.items(), key=lambda x: x[1], reverse=True):
            marcador = "✓ TRAMO" if "TRAMO" in capa.upper() else "  "
            print(f"   {marcador} {capa}: {cantidad} polilínea(s)")

        # Identificar capas potenciales
        capas_tramo = [c for c in capas_dict.keys() if "TRAMO" in c.upper()]
        print(f"\n[3] Capas que contienen 'TRAMO': {len(capas_tramo)}")

        if not capas_tramo:
            print("SUGERENCIA: No se encontraron capas con 'TRAMO' en el nombre")
            print("Verifica el nombre de las capas en tu dibujo de AutoCAD")

        print("\n" + "="*60)
        print("TEST DE CAPAS COMPLETADO")
        print("="*60)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    try:
        test_obtener_tramos()
        test_validar_integridad_objetos()
        test_deteccion_capas_personalizadas()

        print("\n" + "="*60)
        print("TODOS LOS TESTS DE AUTOCAD_UTILS COMPLETADOS")
        print("="*60)

    except Exception as e:
        print(f"\nERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
