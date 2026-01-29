"""
Herramienta de Diagnóstico Visual: Dibuja el grafo en AutoCAD
"""

import win32com.client
from optimizer import NetworkGraph


def dibujar_grafo_debug(grafo, acad):
    """
    Dibuja los nodos y aristas del grafo en una capa de diagnóstico.
    """
    CAPA_DEBUG = "DEBUG_GRAFO_NODOS"
    CAPA_ARISTAS = "DEBUG_GRAFO_CONEXIONES"

    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # Crear capas de debug (Color 1=Rojo, 6=Magenta)
    try:
        l1 = doc.Layers.Add(CAPA_DEBUG)
        l1.Color = 1
        l2 = doc.Layers.Add(CAPA_ARISTAS)
        l2.Color = 6
    except Exception:
        pass

    print(f"Dibujando {len(grafo.nodes)} nodos y sus conexiones...")

    # Dibujar Nodos (Círculos)
    # Usamos transacción o simplemente iteramos (win32com es rápido)
    radio_nodo = 0.2  # Ajustar según escala

    for key, coords in grafo.nodes.items():
        # coords es (x, y)
        center = win32com.client.VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, (coords[0], coords[1], 0.0)
        )
        circulo = msp.AddCircle(center, radio_nodo)
        circulo.Layer = CAPA_DEBUG

    # Dibujar Aristas (Líneas)
    # Para no dibujar doble (A->B y B->A), llevamos un registro
    dibujados = set()

    for nodo_id, vecinos in grafo.adj.items():
        origen = grafo.nodes[nodo_id]

        for vecino_id, peso in vecinos:
            # Crear ID único para la arista (menor, mayor)
            edge_id = tuple(sorted((nodo_id, vecino_id)))

            if edge_id not in dibujados:
                destino = grafo.nodes[vecino_id]

                # Crear línea
                start = win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8, (origen[0], origen[1], 0.0)
                )
                end = win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8, (destino[0], destino[1], 0.0)
                )

                linea = msp.AddLine(start, end)
                linea.Layer = CAPA_ARISTAS

                dibujados.add(edge_id)

    print("Visualización completada. Revisa las capas 'DEBUG_GRAFO...'")


# BLOQUE PARA PROBARLO
if __name__ == "__main__":
    import pythoncom

    # Configuración (mover a config.yaml)
    CAPA_RED = "CAT_LINEA DE RED EXISTENTE"
    TOLERANCIA_SNAP = 0.05

    try:
        # Conexión a AutoCAD
        acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.ActiveDocument
        msp = doc.ModelSpace

        print(f"Construyendo grafo desde capa '{CAPA_RED}'...")

        # Inicializar el Grafo
        grafo = NetworkGraph(tolerance=TOLERANCIA_SNAP)

        # Llenar el grafo con las líneas del plano
        count = 0
        for i in range(msp.Count):
            obj = msp.Item(i)
            try:
                # Solo procesamos líneas de la capa de red
                if (
                    obj.ObjectName == "AcDbLine"
                    and obj.Layer.upper() == CAPA_RED.upper()
                ):
                    # Extraer puntos start/end
                    p1 = obj.StartPoint
                    p2 = obj.EndPoint

                    # Convertir a tuplas (x, y) ignorando Z
                    start = (p1[0], p1[1])
                    end = (p2[0], p2[1])

                    grafo.add_line(start, end)
                    count += 1
            except Exception:
                continue

        print(f"    -> {count} líneas procesadas.")
        print(f"    -> {len(grafo.nodes)} nodos detectados.")

        # Dibujar el debug
        if count > 0:
            dibujar_grafo_debug(grafo, acad)
        else:
            print("No se encontraron líneas. Verifica el nombre de la capa CAPA_RED.")

    except Exception as e:
        print(f"Error crítico: {e}")
