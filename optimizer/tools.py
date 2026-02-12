"""
Módulo de Herramientas de Diagnóstico y Utilidades Varias.
Aloja funcionalidades puntuales invocadas desde la GUI.
"""

import win32com.client
import pythoncom
from .acad_interface import get_acad_com
from .acad_block_reader import extract_specific_blocks
from .config_loader import get_config
from .feedback_logger import logger
from .utils_math import distancia_euclidiana


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

    # Capa temporal para visualización
    capa_visual = "DEBUG_DIRECCION_TRAMOS"
    try:
        acad.ActiveDocument.Layers.Add(capa_visual).Color = 6  # Magenta
    except Exception:
        pass

    count = 0
    radio_marca = 1.0  # Ajustable

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
                    win32com.client.VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8, p_fin
                    ),
                    radio_marca,
                )

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
                c_fin.Color = 1  # Rojo
                c_fin.Layer = capa_visual

                count += 1
        except Exception:
            continue

    logger.info(
        f"Visualización de extremos: {count} polilíneas marcadas en capa '{capa_visual}'."
    )
    return f"Se marcaron {count} tramos."


def herramienta_inventario_rapido() -> str:
    """
    Escanea el dibujo y cuenta los bloques configurados en el YAML.
    Retorna un string con el resumen.
    """
    # Obtener lista plana de todos los equipos configurados
    dic_equipos = get_config("equipos", {})
    target_names = []
    for lista in dic_equipos.values():
        target_names.extend(lista)

    if not target_names:
        return "No hay equipos configurados en config.yaml"

    logger.info("Iniciando inventario de bloques...")
    bloques = extract_specific_blocks(target_names)

    conteo = {}
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

    # CONFIGURACIÓN (Idealmente mover a config.yaml)
    RADIO = 20.0
    LAYER_TEXTOS = "HUB_BOX_3.5_P"  # OJO: Ajustar a tu capa real
    BLOQUE_HUB = "HBOX_3.5P"

    hubs = []
    textos = []

    # 1. Escaneo
    for i in range(msp.Count):
        try:
            obj = msp.Item(i)
            if obj.ObjectName == "AcDbBlockReference":
                name = obj.EffectiveName if hasattr(obj, "EffectiveName") else obj.Name
                if name == BLOQUE_HUB:
                    hubs.append(obj)
            elif obj.ObjectName in ["AcDbText", "AcDbMText"]:
                if obj.Layer == LAYER_TEXTOS:
                    textos.append(obj)
        except Exception:
            pass

    if not hubs:
        return "No se encontraron bloques HUB."

    # 2. Asociación
    reporte = f"Hubs: {len(hubs)} | Textos: {len(textos)}\n"
    asociados = 0

    for hub in hubs:
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
            reporte += (
                f"✅ Hub en {p_hub[0]:.0f},{p_hub[1]:.0f} -> '{mejor_txt.TextString}'\n"
            )
            asociados += 1
        else:
            reporte += f"⚠️ Hub en {p_hub[0]:.0f},{p_hub[1]:.0f} -> SIN TEXTO CERCA\n"

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
        reporte += f"• {b['name']} (H:{b['handle']}) -> ID: {id_name}\n"

    return reporte


def garantizar_capa_existente(doc, nombre_capa, color_id: int = 7) -> str:
    """
    Verifica si una capa existe en el documento. Si no, la crea.
    Retorna el nombre de la capa validado.
    """
    try:
        doc.Layers.Item(nombre_capa)
    except Exception:
        try:
            nueva_capa = doc.Layers.Add(nombre_capa)
            nueva_capa.Color = color_id
        except Exception as e:
            logger.error(f"No se pudo crear la capa '{nombre_capa}': {e}")
            pass

    return nombre_capa
