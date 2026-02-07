import win32com.client
from optimizer.utils_math import distancia_euclidiana


def main():
    print("--- ASOCIACIÓN HUB -> TEXTO CERCANO ---")
    acad = win32com.client.Dispatch("AutoCAD.Application")
    msp = acad.ActiveDocument.ModelSpace

    RADIO_BUSQUEDA = 20.0  # Metros de busqueda
    LAYER_TEXTOS = "HUB_BOX_3.5_P"  # Capa donde están los nombres
    BLOQUE_HUB = "HBOX_3.5P"  # Nombre de tu bloque HUB

    hubs = []
    textos = []

    # Barrido único para separar Hubs y Textos (Eficiencia)
    print("Escaneando dibujo...")
    for i in range(msp.Count):
        obj = msp.Item(i)

        # Guardar HUBS
        if obj.ObjectName == "AcDbBlockReference":
            nombre = obj.EffectiveName if hasattr(obj, "EffectiveName") else obj.Name
            if nombre == BLOQUE_HUB:
                hubs.append(obj)

        # Guardar TEXTOS
        elif obj.ObjectName in ["AcDbText", "AcDbMText"]:
            if obj.Layer == LAYER_TEXTOS:
                textos.append(obj)

    print(f"Hubs encontrados: {len(hubs)}")
    print(f"Textos candidatos: {len(textos)}")

    # 2. Algoritmo de Asociación
    for hub in hubs:
        ins_pt = hub.InsertionPoint
        p_hub = (ins_pt[0], ins_pt[1])

        mejor_texto = None
        mejor_dist = float("inf")

        for txt in textos:
            ins_txt = txt.InsertionPoint
            p_txt = (ins_txt[0], ins_txt[1])

            dist = distancia_euclidiana(p_hub, p_txt)

            if dist < RADIO_BUSQUEDA and dist < mejor_dist:
                mejor_dist = dist
                mejor_texto = txt

        if mejor_texto:
            contenido = mejor_texto.TextString
            print(
                f"✅ HUB en {p_hub} asociado con: '{contenido}' (Dist: {mejor_dist:.2f}m)"
            )

            # AQUÍ SE PUEDE GUARDAR ESTA ASOCIACIÓN EN EL REPORTE
            # O INCLUSO RENOMBRAR UN ATRIBUTO DEL HUB CON ESTE TEXTO
        else:
            print(f"⚠️ HUB en {p_hub} SIN NOMBRE (Nada cerca en {RADIO_BUSQUEDA}m)")


if __name__ == "__main__":
    main()
