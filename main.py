import math
import win32com.client
import pythoncom
from optimizer import extract_specific_blocks, seleccionar_cable, NetworkGraph
from optimizer.acad_utils import get_acad_com
from optimizer.topology import calcular_ruta_completa
from optimizer.config_loader import get_config


def dibujar_debug(msp, puntos, color=1, offset_dist=0.5):
    """Dibuja una polilínea de depuración en AutoCAD."""
    distancia = get_config("rutas.offset_visual_debug", 0.5)
    layer_name = get_config("rutas.capa_debug", "DEBUG_RUTAS")

    if not puntos or len(puntos) < 2:
        return

    vertices = []
    for p in puntos:
        vertices.extend([p[0], p[1]])

    try:
        vertices_var = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, vertices
        )
        pline = msp.AddLightWeightPolyline(vertices_var)

        try:
            nuevos_objs = pline.Offset(distancia)
            pline.Delete()
            target = nuevos_objs[0]
        except Exception:
            target = pline

        target.Layer = layer_name
        target.Color = color

    except Exception as e:
        print(f"Error dibujando debug: {e}")


def insertar_texto_paralelo(msp, p1, p2, texto, offset=1.5, altura=1.0):
    """
    Inserta texto alineado con el segmento p1->p2 y desplazado perpendicularmente.
    Maneja la rotación para que el texto nunca quede "cabeza abajo".
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    angulo = math.atan2(dy, dx)

    texto_invertido = False
    if abs(angulo) > math.pi / 2:
        angulo += math.pi
        texto_invertido = True

    mid_x = (p1[0] + p2[0]) / 2
    mid_y = (p1[1] + p2[1]) / 2

    longitud = math.hypot(dx, dy)
    if longitud == 0:
        return  # Evitar división por cero

    signo_offset = -1 if texto_invertido else 1

    off_x = (-dy / longitud) * offset * signo_offset
    off_y = (dx / longitud) * offset * signo_offset

    pos_final_x = mid_x + off_x
    pos_final_y = mid_y + off_y

    insert_pt = win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8, (pos_final_x, pos_final_y, 0)
    )
    txt_obj = msp.AddText(texto, insert_pt, altura)

    txt_obj.Rotation = angulo

    txt_obj.Alignment = 13
    txt_obj.TextAlignmentPoint = insert_pt  # Necesario al cambiar Alignment

    return txt_obj


def main():
    print("--- INICIANDO OPTIMIZADOR HÍBRIDO ---")

    acad = get_acad_com()
    if not acad:
        return
    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # YAML
    CAPA_RED = get_config("rutas.capa_red_vial")
    CAPA_TRAMO = get_config("rutas.capa_tramos_logicos")

    # Construir Grafo de 'LINEA DE RED'
    print("[1/3] Leyendo LINEA DE RED...")
    grafo = NetworkGraph(tolerance=0.1)

    count_lines = 0
    # Iteración optimizada para COM
    for i in range(msp.Count):
        obj = msp.Item(i)
        if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == CAPA_RED:
            p1 = obj.StartPoint
            p2 = obj.EndPoint
            grafo.add_line((p1[0], p1[1]), (p2[0], p2[1]))
            count_lines += 1

    print(f" -> {count_lines} calles indexadas. {len(grafo.nodes)} nodos.")

    # Ingesta: Leer Equipos
    print("[2/3] Indexando equipos...")
    bloques = extract_specific_blocks(
        ["X_BOX_P", "HBOX_3.5P", "FAT_INT_3.0_P", "FAT_FINAL_3.0_P"]
    )
    print(f"-> {len(bloques)} equipos encontrados.")

    # Procesar TRAMOS (Interacción Usuario)
    print("[3/3] Procesando capa 'TRAMO'...")

    # Crear capa debug si no existe
    try:
        doc.Layers.Add(get_config("rutas.capa_debug"))
    except Exception:
        pass

    count_ok = 0
    for i in range(msp.Count):
        obj = msp.Item(i)
        if obj.ObjectName == "AcDbPolyline" and obj.Layer.upper() == CAPA_TRAMO:
            coords = obj.Coordinates
            if len(coords) < 4:
                continue  # Mal dibujada

            p_start = (coords[0], coords[1])
            p_end = (coords[-2], coords[-1])  # Último punto

            dist_real, ruta_visual, meta = calcular_ruta_completa(
                p_start, p_end, grafo, bloques
            )

            if dist_real:
                print(f"  ✓ Ruta {meta['origen']} -> {meta['destino']}")
                print(f"   Dist. Dibujo: {obj.Length:.1f}m | REAL: {dist_real:.1f}m")

                # Seleccionar Cable
                # NOTA: Debes adaptar seleccionar_cable para recibir nombres de equipos si quieres reglas complejas
                # Por ahora usamos una regla genérica basada en nombre de equipo
                count_ok += 1
                tipo_cable = "xbox_hub" if "X_BOX" in meta["origen"] else "distribucion"
                cable_item, reserva = seleccionar_cable(dist_real, tipo_cable)

                print(f"     Cable: {cable_item}m (Reserva: {reserva:.1f}m)")

                # Dibujar ruta debug
                dibujar_debug(msp, ruta_visual)

                # Etiquetar en dibujo
                idx = len(ruta_visual) // 2
                p_a = ruta_visual[idx]
                p_b = ruta_visual[idx + 1]
                texto_final = f"CABLE {cable_item}m | L.Real: {dist_real:.1f}m | Res: {reserva:.1f}m"
                insertar_texto_paralelo(msp, p_a, p_b, texto_final, offset=1.5)

            else:
                print(f"   X Error en tramo handle {obj.Handle}: {meta}")

    print(f"\n--- PROCESO FINALIZADO: {count_ok} tramos procesados ---")


if __name__ == "__main__":
    main()
