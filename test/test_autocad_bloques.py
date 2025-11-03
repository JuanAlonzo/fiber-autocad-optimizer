"""
Test para detección de bloques en AutoCAD
Valida la identificación de X_BOX, HUB_BOX, FAT_INT y la lógica de tipo de tramo
"""
import sys

from pyautocad import Autocad, APoint

from optimizer import log_error, log_info, log_warning


def obtener_bloques(nombres_bloques=None):
    """
    Detecta bloques específicos en el dibujo AutoCAD

    Args:
        nombres_bloques: Lista de nombres de bloques a buscar
                        Default: ["X_BOX_P", "HUB_BOX_3.5_P", "FAT_INT_3.0_P", "FAT_FINAL_3.0_P"]

    Returns:
        Lista de diccionarios con información de cada bloque
    """
    if nombres_bloques is None:
        nombres_bloques = ["X_BOX_P", "HBOX_3.5P",
                           "FAT_INT_3.0_P", "FAT_FINAL_3.0_P"]

    try:
        acad = Autocad(create_if_not_exists=True)
        bloques = []

        log_info(f"Buscando bloques: {', '.join(nombres_bloques)}")

        # Iterar sobre todos los objetos del modelo
        for ent in acad.iter_objects():
            try:
                # Verificar si es un bloque
                if ent.ObjectName == 'AcDbBlockReference':
                    nombre_bloque = ent.Name.upper()

                    # Verificar si es uno de los bloques buscados
                    if any(nb.upper() == nombre_bloque for nb in nombres_bloques):
                        try:
                            pos = ent.InsertionPoint
                            bloques.append({
                                "nombre": ent.Name,
                                "posicion": (pos[0], pos[1]),
                                "handle": ent.Handle,
                                "layer": ent.Layer,
                                "obj": ent
                            })
                            print(
                                f"Bloque encontrado: {ent.Name} en ({pos[0]:.2f}, {pos[1]:.2f}) | Layer: {ent.Layer}")
                        except Exception as e:
                            log_warning(
                                f"Error al leer propiedades del bloque {nombre_bloque}: {e}")
                            continue
            except Exception as e:
                # Silenciar errores de objetos que no se pueden leer
                continue

        log_info(f"Total de bloques encontrados: {len(bloques)}")
        return bloques

    except Exception as e:
        log_error(f"Error al conectar con AutoCAD: {e}")
        return []


def identificar_tipo_tramo(bloque_origen, bloque_destino):
    """
    Identifica el tipo de tramo basado en bloques de origen y destino

    Args:
        bloque_origen: Diccionario con info del bloque origen
        bloque_destino: Diccionario con info del bloque destino

    Returns:
        str: "xbox_hub", "hub_fat", "expansion", o "desconocido"
    """
    origen = bloque_origen["nombre"].upper()
    destino = bloque_destino["nombre"].upper()

    # XBOX → HUB_BOX
    if "X_BOX_P" in origen and "HBOX_3.5P" in destino:
        return "xbox_hub"

    # HUB_BOX → FAT
    if "HBOX_3.5P" in origen and "FAT_INT_3.0_P" in destino:
        return "hub_fat"

    # FAT → FAT (expansión)
    if "FAT_INT_3.0_P" in origen and "FAT_INT_3.0_P" in destino:
        return "expansion"

    # FAT → FAT FINAL (expansión)
    if "FAT_INT_3.0_P" in origen and "FAT_FINAL_3.0_P" in destino:
        return "expansion"

    return "desconocido"


def calcular_distancia(pos1, pos2):
    """
    Calcula la distancia euclidiana entre dos puntos

    Args:
        pos1: tupla (x, y)
        pos2: tupla (x, y)

    Returns:
        float: distancia en unidades del dibujo
    """
    import math
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx**2 + dy**2)


def encontrar_bloque_mas_cercano(bloque_origen, bloques_candidatos):
    """
    Encuentra el bloque más cercano al bloque de origen

    Args:
        bloque_origen: Diccionario con info del bloque origen
        bloques_candidatos: Lista de bloques candidatos

    Returns:
        Diccionario del bloque más cercano o None
    """
    if not bloques_candidatos:
        return None

    pos_origen = bloque_origen["posicion"]

    bloque_mas_cercano = None
    distancia_minima = float('inf')

    for bloque in bloques_candidatos:
        distancia = calcular_distancia(pos_origen, bloque["posicion"])
        if distancia < distancia_minima:
            distancia_minima = distancia
            bloque_mas_cercano = bloque

    return bloque_mas_cercano


def test_deteccion_bloques():
    """Test principal de detección de bloques"""
    print("\n" + "="*60)
    print("TEST: DETECCIÓN DE BLOQUES EN AUTOCAD")
    print("="*60)

    # Test 1: Buscar todos los bloques
    print("\n[1] Buscando todos los bloques X_BOX_P, HBOX_3.5P, FAT_INT_3.0_P y FAT_FINAL_3.0_P...")
    bloques = obtener_bloques()

    if not bloques:
        print("NO SE ENCONTRARON BLOQUES")
        print("Asegúrate de que el dibujo de AutoCAD esté abierto")
        print("y contenga bloques con nombres: X_BOX_P, HBOX_3.5P, FAT_INT_3.0_P y FAT_FINAL_3.0_P")
        return

    # Clasificar bloques por tipo
    xbox_blocks = [b for b in bloques if "X_BOX_P" in b["nombre"].upper()]
    hub_blocks = [b for b in bloques if "HBOX_3.5P" in b["nombre"].upper()]
    fat_blocks = [b for b in bloques if "FAT_INT_3.0_P" in b["nombre"].upper()]
    fat_final_blocks = [
        b for b in bloques if "FAT_FINAL_3.0_P" in b["nombre"].upper()]

    print(f"\nRESUMEN:")
    print(f"   X_BOX_P: {len(xbox_blocks)}")
    print(f"   HBOX_3.5P: {len(hub_blocks)}")
    print(f"   FAT_INT_3.0_P: {len(fat_blocks)}")
    print(f"   FAT_FINAL_3.0_P: {len(fat_final_blocks)}")
    print(f"   TOTAL: {len(bloques)}")

    # Test 2: Identificar tipos de tramos
    if len(bloques) >= 2:
        print(f"\n[2] Identificando tipos de tramos entre bloques...")

        # Ejemplo: X_BOX → HUB_BOX
        if xbox_blocks and hub_blocks:
            tipo = identificar_tipo_tramo(xbox_blocks[0], hub_blocks[0])
            print(
                f"✓ {xbox_blocks[0]['nombre']} → {hub_blocks[0]['nombre']}: '{tipo}'")
            assert tipo == "xbox_hub", f"Expected 'xbox_hub', got '{tipo}'"

        # Ejemplo: HUB_BOX → FAT
        if hub_blocks and fat_blocks:
            tipo = identificar_tipo_tramo(hub_blocks[0], fat_blocks[0])
            print(
                f"✓ {hub_blocks[0]['nombre']} → {fat_blocks[0]['nombre']}: '{tipo}'")
            assert tipo == "hub_fat", f"Expected 'hub_fat', got '{tipo}'"

        # Ejemplo: FAT → FAT
        if len(fat_blocks) >= 2:
            tipo = identificar_tipo_tramo(fat_blocks[0], fat_blocks[1])
            print(
                f"✓ {fat_blocks[0]['nombre']} → {fat_blocks[1]['nombre']}: '{tipo}'")
            assert tipo == "expansion", f"Expected 'expansion', got '{tipo}'"

    # Test 3: Calcular distancias
    if len(bloques) >= 2:
        print(f"\n[3] Calculando distancias entre bloques...")
        dist = calcular_distancia(
            bloques[0]["posicion"], bloques[1]["posicion"])
        print(
            f"✓ Distancia entre {bloques[0]['nombre']} y {bloques[1]['nombre']}: {dist:.2f} unidades")

    # Test 4: Encontrar bloque más cercano
    if xbox_blocks and hub_blocks:
        print(f"\n[4] Buscando HUB_BOX_3.5_P más cercano a X_BOX_P...")
        mas_cercano = encontrar_bloque_mas_cercano(xbox_blocks[0], hub_blocks)
        if mas_cercano:
            dist = calcular_distancia(
                xbox_blocks[0]["posicion"], mas_cercano["posicion"])
            print(
                f"✓ HUB_BOX_3. más cercano: {mas_cercano['nombre']} a {dist:.2f} unidades")

    print("\n" + "="*60)
    print("TEST DE BLOQUES COMPLETADO")
    print("="*60)


if __name__ == "__main__":
    try:
        test_deteccion_bloques()
    except Exception as e:
        print(f"\nERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
