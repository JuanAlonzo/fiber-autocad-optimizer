from optimizer import get_acad_com


def main():
    print("--- TEST DE MUTACIÓN DE CAPAS ---")
    acad = get_acad_com()
    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # Capa origen
    C_ORIGEN = "TRAMO"

    # Capas destino (Crearlas si no existen)
    C_CORTA = "CABLE PRECONECT 2H SM (100M)"  # < 150m
    C_LARGA = "CABLE PRECONECT 2H SM (200M)"  # > 150m

    count = 0
    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            if obj.ObjectName == "AcDbPolyline" and obj.Layer.upper() == C_ORIGEN:
                longitud = obj.Length

                # Lógica simple de decisión
                if longitud > 150.0:
                    obj.Layer = C_LARGA
                    print(f"Handle {obj.Handle}: {longitud:.1f}m -> TRONCAL")
                else:
                    obj.Layer = C_CORTA
                    print(f"Handle {obj.Handle}: {longitud:.1f}m -> DISTRIBUCION")

                obj.ConstantWidth = 0.5
                obj.LinetypeScale = 4

                count += 1
        except Exception as e:
            print(f"Error procesando objeto index {i}: {e}")
            continue

    print(f"Se actualizaron {count} elementos.")
    # Refrescar pantalla de AutoCAD
    doc.Regen(1)


if __name__ == "__main__":
    main()
