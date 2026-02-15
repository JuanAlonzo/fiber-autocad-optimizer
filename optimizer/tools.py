"""
Módulo de Herramientas de Diagnóstico y Utilidades Varias.
Aloja funcionalidades puntuales invocadas desde la GUI.
"""

from typing import Optional, Any, List, Dict
import win32com.client
from .acad_interface import get_acad_com
from .acad_block_reader import extract_specific_blocks
from .config_loader import get_config
from .acad_geometry import NetworkGraph
from .acad_drawer import dibujar_grafo_completo
from .constants import ASI, SysLayers, Geometry
from .feedback_logger import logger
from .utils_math import distancia_euclidiana


def garantizar_capa_existente(
    doc: Any, nombre_capa: str, color_id: int = ASI.BLANCO
) -> Optional[str]:
    """
    Verifica si una capa existe en el documento. Si no, la crea.
    Args:
        doc: Documento activo de AutoCAD.
        nombre_capa: Nombre de la capa deseada.
        color_id: Color ACI por defecto (7 = Blanco/Negro).
    Returns:
        str: El nombre de la capa si todo salió bien, o None si falló.
    """
    try:
        doc.Layers.Item(nombre_capa)
    except Exception:
        try:
            nueva_capa = doc.Layers.Add(nombre_capa)
            nueva_capa.Color = color_id
            return nombre_capa
        except Exception as e:
            logger.error(f"No se pudo crear la capa '{nombre_capa}': {e}")
            return None

    return nombre_capa


def herramienta_visualizar_extremos() -> str:
    """
    Dibuja círculos verdes (INI) y rojos (FIN) en las polilíneas de la capa TRAMO.
    Ayuda a identificar si se dibujaron en el sentido correcto.
    """
    acad = get_acad_com()
    if not acad:
        logger.error("No se pudo conectar a AutoCAD.")
        return "Error de conexión"

    msp = acad.ActiveDocument.ModelSpace
    capa_tramo = get_config("rutas.capa_tramos_logicos", "TRAMO")

    garantizar_capa_existente(
        acad.ActiveDocument, SysLayers.TEMPORAL_EXTREMOS, ASI.MAGENTA
    )

    count = 0
    import pythoncom

    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            if obj.ObjectName == "AcDbPolyline" and obj.Layer.upper() == capa_tramo:
                coords = obj.Coordinates
                if len(coords) < 4:
                    continue

                # Puntos 2D
                p_ini = (coords[0], coords[1], 0.0)
                p_fin = (coords[-2], coords[-1], 0.0)

                # Dibujar INICIO (Verde)
                c_ini = msp.AddCircle(
                    win32com.client.VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8, p_ini
                    ),
                    Geometry.RADIO_INI_FIN,
                )
                t_ini = msp.AddText(
                    "INI",
                    win32com.client.VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8,
                        (p_ini[0] + 1, p_ini[1] + 1, 0),
                    ),
                    1.5,
                )
                t_ini.Color = ASI.VERDE
                t_ini.Layer = SysLayers.TEMPORAL_EXTREMOS
                c_ini.Color = ASI.VERDE
                c_ini.Layer = SysLayers.TEMPORAL_EXTREMOS

                # Dibujar FIN (Rojo)
                c_fin = msp.AddCircle(
                    win32com.client.VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8, p_fin
                    ),
                    Geometry.RADIO_INI_FIN,
                )

                t_fin = msp.AddText(
                    "FIN",
                    win32com.client.VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8,
                        (p_fin[0] + 1, p_fin[1] + 1, 0),
                    ),
                    1.5,
                )
                t_fin.Color = ASI.ROJO
                t_fin.Layer = SysLayers.TEMPORAL_EXTREMOS
                c_fin.Color = ASI.ROJO
                c_fin.Layer = SysLayers.TEMPORAL_EXTREMOS

                count += 1
        except Exception:
            continue

    logger.info(
        f"Visualización de extremos: {count} polilíneas marcadas en capa '{SysLayers.TEMPORAL_EXTREMOS}'."
    )
    return f"Se marcaron {count} tramos."


def herramienta_inventario_rapido() -> str:
    """
    Escanea el dibujo y cuenta los bloques configurados en el YAML.
    Returns:
        str: Reporte formateado para mostrar al usuario.
    """
    dic_equipos: Dict[str, List[str]] = get_config("equipos", {})
    target_names: List[str] = []
    for lista in dic_equipos.values():
        target_names.extend(lista)

    if not target_names:
        return "No hay equipos configurados en config.yaml"

    logger.info("Iniciando inventario de bloques...")
    bloques = extract_specific_blocks(target_names)

    conteo: Dict[str, int] = {}
    for b in bloques:
        nombre = b["name"]
        conteo[nombre] = conteo.get(nombre, 0) + 1

    # Formatear reporte
    reporte = "--- INVENTARIO DE EQUIPOS ---\n"
    if not conteo:
        reporte += "No se encontraron bloques conocidos."
    else:
        for nombre, cantidad in sorted(conteo.items()):
            reporte += f"• {nombre}: {cantidad}\n"

    logger.info(f"Inventario finalizado. Total: {len(bloques)}")
    return reporte


def herramienta_asociar_hubs() -> str:
    """
    Busca bloques HUB y textos cercanos para 'adivinar' su nombre.
    Retorna un reporte de texto.
    """
    acad = get_acad_com()
    if not acad:
        return "Error: No AutoCAD"
    msp = acad.ActiveDocument.ModelSpace

    # CONFIG
    hbox_validos = get_config("equipos.hbox", [])
    RADIO = get_config("tolerancias.radio_busqueda_acceso", 20.0)
    capa_textos = get_config("rutas.capa_textos_hubs", "HUB_BOX_3.5_P")

    hubs = []
    textos = []

    if not hbox_validos:
        return "No hay bloque 'hbox' configurado en config.yaml"

    # Escaneo
    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            nombre_obj = obj.ObjectName

            if nombre_obj == "AcDbBlockReference":
                name = obj.EffectiveName if hasattr(obj, "EffectiveName") else obj.Name
                if name in hbox_validos:
                    hubs.append(obj)

            elif nombre_obj in ["AcDbText", "AcDbMText"]:
                if capa_textos is None or obj.Layer == capa_textos:
                    textos.append(obj)
        except Exception:
            pass

    if not hubs:
        return f"No se encontraron bloques '{hbox_validos}'."

    # 2. Asociación
    reporte = f"Hubs encontrados: {len(hubs)} | Textos encontrados: {len(textos)}\n\n"
    asociados = 0

    for hub in hubs:
        try:
            ins = hub.InsertionPoint
            p_hub = (ins[0], ins[1])
            mejor_txt = None
            min_dist = RADIO

            for txt in textos:
                t_ins = txt.InsertionPoint
                d = distancia_euclidiana(p_hub, (t_ins[0], t_ins[1]))
                if d < min_dist:
                    min_dist = d
                    mejor_txt = txt

            if mejor_txt:
                texto_limpio = mejor_txt.TextString.strip()
                reporte += f"Hub ({hub.Name}) en ({p_hub}) -> '{texto_limpio}'\n"
                asociados += 1
            else:
                reporte += f"Hub ({hub.Name}) en ({p_hub}) -> SIN TEXTO (<{RADIO}m)\n"
        except Exception as e:
            logger.debug(f"Error al asociar hub: {e}")

    return f"Asociación terminada ({asociados}/{len(hubs)}).\n\n{reporte}"


def herramienta_analizar_fat() -> str:
    """
    Lista los atributos ID_NAME de las FATs encontradas.
    """
    nombres_fat = ["FAT_INT_3.0_P", "FAT_FINAL_3.0_P"]  # Agregar más si es necesario
    bloques = extract_specific_blocks(nombres_fat)

    if not bloques:
        return "No se encontraron FATs."

    reporte = "--- ANÁLISIS FAT ---\n"
    for b in bloques:
        # Intentar buscar atributo ID_NAME o similar
        attrs = b.get("attributes", {})
        id_name = attrs.get("ID_NAME", "S/N")
        reporte += f"• {b['name']} -> {id_name}\n"

    return reporte


def herramienta_dibujar_grafo_vial() -> str:
    """
    Construye y dibuja el grafo de la red vial en el plano actual.
    """
    acad = get_acad_com()
    if not acad:
        return "Error: No hay conexión con AutoCAD."

    doc = acad.ActiveDocument
    msp = doc.ModelSpace

    # 1. Preparar capas visuales
    garantizar_capa_existente(doc, SysLayers.DEBUG_NODOS, ASI.CYAN)
    garantizar_capa_existente(doc, SysLayers.DEBUG_ARISTAS, ASI.GRIS)

    # 2. Construir Grafo
    logger.info("Leyendo red vial para visualización...")
    capa_red = get_config("rutas.capa_red_vial")
    tol = get_config("tolerancias.snap_grafo_vial", 0.1)

    grafo = NetworkGraph(tolerance=tol)

    count = 0
    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            if obj.ObjectName == "AcDbLine" and obj.Layer.upper() == capa_red:
                grafo.add_line(obj.StartPoint[:2], obj.EndPoint[:2])
                count += 1
        except Exception:
            pass

    if count == 0:
        return f"No se encontraron líneas en la capa '{capa_red}'."

    # 3. Dibujar
    logger.info(f"Dibujando {len(grafo.nodes)} nodos y sus conexiones...")
    dibujar_grafo_completo(msp, grafo)

    return (
        f"Grafo dibujado.\nLíneas procesadas: {count}\nNodos únicos: {len(grafo.nodes)}"
    )
