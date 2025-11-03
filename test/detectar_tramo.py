from pyautocad import Autocad, APoint


def obtener_tramos_por_capa(nombre_capa="TRAMO"):
    acad = Autocad(create_if_not_exists=True)
    print(f"\nBuscando entidades en la capa '{nombre_capa}'...")

    tramos = []
    for ent in acad.iter_objects("AcDbPolyline"):
        try:
            capa_ent = ent.Layer.upper().strip()
            if capa_ent == nombre_capa.upper():
                longitud = ent.Length
                handle = ent.Handle
                tramos.append((handle, longitud))
                print(
                    f"Tramo encontrado: Handle={handle} | Longitud={round(longitud, 2)}")
        except Exception as e:
            print(f"Error al leer una entidad: {e}")

    print(f"\nTotal de tramos encontrados en '{nombre_capa}': {len(tramos)}")
    return tramos


if __name__ == "__main__":
    obtener_tramos_por_capa("TRAMO")
