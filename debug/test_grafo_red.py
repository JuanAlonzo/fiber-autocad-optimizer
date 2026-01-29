"""
Test de Inteligencia Topológica: Grafo de Red
Reconoce caminos reales usando líneas sueltas (AcDbLine).
"""

import win32com.client
from optimizer import (
    extract_specific_blocks,
    NetworkGraph,
)


def get_start_end_points(obj):
    """Extrae puntos de AcDbLine."""
    try:
        # AcDbLine tiene StartPoint y EndPoint como tuplas (x, y, z)
        p1 = obj.StartPoint
        p2 = obj.EndPoint
        return (p1[0], p1[1]), (p2[0], p2[1])
    except Exception:
        return None, None


def test_navegacion_red():
    # Agregar variables de configuración a config.yaml en el futuro
    CAPA_RED = "CAT_LINEA DE RED EXISTENTE"  # Ajustar nombre
    TOLERANCIA_SNAP = (
        0.05  # 5cm de tolerancia para unir líneas que no se tocan perfecto
    )
    RADIO_BUSQUEDA = 10.0  # El equipo debe estar a máx 10m de algún nodo de la red

    print("Construyendo el Grafo de la Red (Cargando líneas... espera un momento)")

    acad = win32com.client.Dispatch("AutoCAD.Application")
    msp = acad.ActiveDocument.ModelSpace
    grafo = NetworkGraph(tolerance=TOLERANCIA_SNAP)

    lineas_count = 0
    for i in range(msp.Count):
        obj = msp.Item(i)
        try:
            # ACEPTAMOS SOLO LÍNEAS (AcDbLine)
            if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == CAPA_RED.upper():
                p1, p2 = get_start_end_points(obj)
                if p1 and p2:
                    grafo.add_line(p1, p2)
                    lineas_count += 1
        except Exception:
            continue

    print(f"    -> {lineas_count} líneas procesadas e integradas al mapa virtual.")
    print(f"    -> {len(grafo.nodes)} nodos únicos detectados (intersecciones/puntas).")

    print("\n2. Ubicando equipos en el mapa...")
    bloques = extract_specific_blocks(["X_BOX_P", "HBOX_3.5P"])

    equipos_en_red = []

    for b in bloques:
        pos = (b["xyz"][0], b["xyz"][1])
        nodo_cercano, dist = grafo.find_nearest_node(pos, max_radius=RADIO_BUSQUEDA)

        estado = "Conectado" if nodo_cercano else "Aislado (Lejos de la red)"
        equipos_en_red.append({"info": b, "nodo": nodo_cercano, "dist_acceso": dist})
        print(f"   - {b['name']} ({b['handle']}): {estado}")

    print("\n3. Test de Rutas (Pathfinding)...")

    # Separamos XBOX y HUBS
    xboxes = [e for e in equipos_en_red if "X_BOX" in e["info"]["name"] and e["nodo"]]
    hubs = [e for e in equipos_en_red if "HBOX" in e["info"]["name"] and e["nodo"]]

    if not xboxes:
        print("No hay XBOX conectados a la red. No se pueden calcular rutas.")
        return

    for xbox in xboxes:
        print(f"\nOrigen: {xbox['info']['name']} (Handle {xbox['info']['handle']})")

        for hub in hubs:
            distancia_red = grafo.get_path_length(xbox["nodo"], hub["nodo"])

            if distancia_red:
                # Distancia total = Distancia en red + Distancia acceso origen + Distancia acceso destino
                total = distancia_red + xbox["dist_acceso"] + hub["dist_acceso"]
                print(f"   -> Hacia {hub['info']['name']} ({hub['info']['handle']}):")
                print(f"      Distancia Real (Ruta): {total:.2f}m")
                print("      ✓ Ruta válida encontrada.")
            else:
                print(
                    f"   -> Hacia {hub['info']['name']}: !!! NO HAY CAMINO (Red desconectada o isla)"
                )


if __name__ == "__main__":
    test_navegacion_red()
