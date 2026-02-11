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
