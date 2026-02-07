import win32com.client


def main():
    print("--- TEST LECTURA/ESCRITURA ATRIBUTOS ---")
    acad = win32com.client.Dispatch("AutoCAD.Application")
    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # 1. Buscar bloques FAT
    print("Buscando bloques FAT...")

    nombres_fat = ["FAT_INT_3.0_P", "FAT_FINAL_3.0_P"]

    count = 0
    for i in range(msp.Count):
        obj = msp.Item(i)
        if obj.ObjectName == "AcDbBlockReference":
            # Verificar nombre efectivo (ignorando prefijos de bloques dinámicos *U)
            nombre = obj.EffectiveName if hasattr(obj, "EffectiveName") else obj.Name

            if nombre in nombres_fat:
                print(f"\nEncontrado: {nombre} (Handle: {obj.Handle})")

                # 2. Leer Atributos
                if obj.HasAttributes:
                    attribs = obj.GetAttributes()
                    for att in attribs:
                        print(f"   - TAG: {att.TagString} | VALOR: {att.TextString}")

                        # --- PRUEBA DE EDICIÓN ---
                        # Ejemplo: Si el atributo es "NOMBRE_FAT", le agregamos un sufijo
                        if (
                            att.TagString == "ID_NAME"
                        ):  # Ajusta este TAG al real de tu bloque
                            nuevo_valor = att.TextString + "_REV"
                            # att.TextString = nuevo_valor  # <--- DESCOMENTAR PARA APLICAR CAMBIO
                            # print(f"     -> CAMBIADO A: {nuevo_valor}")
                            pass
                else:
                    print("   (No tiene atributos editables)")

                count += 1
                if count >= 3:
                    break  # Solo probamos con 3 para no saturar


if __name__ == "__main__":
    main()
