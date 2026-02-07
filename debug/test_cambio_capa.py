import win32com.client


def main():
    print("--- TEST DE MUTACIÓN DE CAPAS ---")
    acad = win32com.client.Dispatch("AutoCAD.Application")
    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # Capa origen
    C_ORIGEN = "CAMBIO_CAPA"

    # Capas destino (Crearlas si no existen)
    C_CORTA = "CABLE PRECONECT 2H SM (100M)"  # < 150m
    C_LARGA = "CABLE PRECONECT 2H SM (200M)"  # > 150m

    # try:
    #     doc.Layers.Add(C_CORTA).Color = 2  # Amarillo
    #     doc.Layers.Add(C_LARGA).Color = 4  # Cian
    # except Exception:
    #     pass

    count = 0
    for i in range(msp.Count):
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

            count += 1

    print(f"Se actualizaron {count} elementos.")
    # Refrescar pantalla de AutoCAD
    doc.Regen(1)


if __name__ == "__main__":
    main()
