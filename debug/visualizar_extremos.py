import win32com.client
import pythoncom
from optimizer.config_loader import get_config


def main():
    print("--- DIAGNÓSTICO DE EXTREMOS Y DIRECCIÓN ---")
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.ActiveDocument
        msp = doc.ModelSpace
    except Exception as e:
        print(f"Error conectando a AutoCAD: {e}")
        return

    capa_tramo = get_config("rutas.capa_tramos_logicos", "TRAMO")
    radio_marca = 1.0  # Tamaño del círculo visual

    count = 0
    print(f"Analizando capa: {capa_tramo}...")

    # Crear capa temporal para el debug visual
    capa_visual = "DEBUG_DIRECCION_TRAMOS"
    try:
        doc.Layers.Add(capa_visual).Color = 6  # Magenta
    except Exception:
        pass

    for i in range(msp.Count):
        obj = msp.Item(i)
        if obj.ObjectName == "AcDbPolyline" and obj.Layer.upper() == capa_tramo:
            coords = obj.Coordinates
            if len(coords) < 4:
                continue

            # Obtener Inicio y Fin
            # Nota: Polyline Coordinates vienen como [x1, y1, x2, y2, ...]
            p_ini = (coords[0], coords[1], 0.0)
            p_fin = (coords[-2], coords[-1], 0.0)

            # Dibujar INICIO (Verde)
            c_ini = msp.AddCircle(
                win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, p_ini),
                radio_marca,
            )
            c_ini.Color = 3  # Verde
            c_ini.Layer = capa_visual

            t_ini = msp.AddText(
                "INI",
                win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8,
                    (p_ini[0] + 1, p_ini[1] + 1, 0),
                ),
                1.5,
            )
            t_ini.Color = 3
            t_ini.Layer = capa_visual

            # Dibujar FIN (Rojo)
            c_fin = msp.AddCircle(
                win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, p_fin),
                radio_marca,
            )
            c_fin.Color = 1  # Rojo
            c_fin.Layer = capa_visual

            t_fin = msp.AddText(
                "FIN",
                win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8,
                    (p_fin[0] + 1, p_fin[1] + 1, 0),
                ),
                1.5,
            )
            t_fin.Color = 1
            t_fin.Layer = capa_visual

            count += 1

    print(f"Procesadas {count} polilíneas. Revisa la capa '{capa_visual}'.")


if __name__ == "__main__":
    main()
