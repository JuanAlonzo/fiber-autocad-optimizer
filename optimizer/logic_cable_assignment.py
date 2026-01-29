"""
Aplica las reglas a cada tramo del dibujo en AutoCAD
"""

import win32com.client
import pythoncom
from .cable_rules import seleccionar_cable, obtener_reserva_requerida
from .text_labels import etiquetar_tramo
from .feedback_logger import log_error, log_warning, log_info
from .config_loader import get_config


def asegurar_capa_existe(acad, nombre_capa):
    """
    Verifica si la capa existe en el documento activo.
    Si no existe (lanza error), la crea automáticamente.
    """
    try:
        # Intentamos acceder a la capa para ver si existe
        acad.doc.Layers.Item(nombre_capa)
    except Exception:
        # Si falla (KeyNotFound), la creamos
        try:
            log_info(f"   [AutoCAD] Creando capa faltante: '{nombre_capa}'")
            acad.doc.Layers.Add(nombre_capa)
        except Exception as e:
            log_warning(f"No se pudo crear la capa '{nombre_capa}': {e}")


def asignar_cables(tramos, tipo_clave, acad):
    """
    Asigna cables a los tramos y actualiza el dibujo de AutoCAD.
    """
    resultados = []
    errores = 0

    reserva_min_necesaria = obtener_reserva_requerida(tipo_clave)

    nombre_cable_real = get_config(
        f"capas_cables.{tipo_clave}.tipo", tipo_clave
    ).upper()

    formato_capa = get_config(
        "general.formato_capa_destino", "CABLE PRECONECT {tipo} SM ({cable}M)"
    )

    log_info(
        f"Procesando {len(tramos)} tramo(s) de tipo '{nombre_cable_real}' (Reserva min: {reserva_min_necesaria}m)"
    )
    capas_verificadas = set()

    for i, tramo in enumerate(tramos, 1):
        try:
            long = tramo["longitud"]
            obj = tramo["obj"]
            handle = tramo["handle"]

            # Determinar cable óptimo
            cable, reserva = seleccionar_cable(long, tipo_clave)

            nueva_capa = formato_capa.format(
                tipo=nombre_cable_real.upper(), cable=cable
            )

            if nueva_capa not in capas_verificadas:
                asegurar_capa_existe(acad, nueva_capa)
                capas_verificadas.add(nueva_capa)

            # Advertir si la reserva es insuficiente
            if reserva < 0:
                log_error(f"Tramo {handle}: Cable insuficiente (falta {-reserva:.2f}m)")
            if reserva < reserva_min_necesaria:
                log_warning(
                    f"Tramo {handle}: Reserva baja ({reserva:.2f}m < {reserva_min_necesaria}m)"
                )

            capa_cambiada = False
            etiqueta_creada = False

            # Intentar cambiar la capa del objeto
            try:
                obj.Layer = nueva_capa
                capa_cambiada = True
            except Exception as e:
                log_warning(f"Tramo {handle}: No se pudo cambiar capa - {str(e)}")

            # Intentar crear etiqueta de texto
            try:
                texto = f"{nombre_cable_real} {cable}M | {round(long, 1)}m | Res: {round(reserva, 1)}m"
                etiquetar_tramo(acad, obj, texto)
                etiqueta_creada = True
            except Exception as e:
                log_warning(f"Tramo {handle}: No se pudo etiquetar - {str(e)}")

            # Registrar resultado (aunque no se haya podido modificar el dibujo)
            resultados.append(
                {
                    "handle": handle,
                    "capa": nueva_capa
                    if capa_cambiada
                    else tramo.get("layer", "DESCONOCIDA"),
                    "longitud": long,
                    "reserva": reserva,
                    "cable": cable,
                    "capa_cambiada": capa_cambiada,
                    "etiqueta_creada": etiqueta_creada,
                }
            )

        except Exception as e:
            errores += 1
            log_error(f"Error procesando tramo {tramo.get('handle', '?')}: {e}")
            continue

    log_info(f"Proceso completado: {len(resultados)} exitosos, {errores} con errores")

    return resultados


def asignar_cables_com(tramos_data, acad_doc):
    """
    tramos_data: Lista de dicts con {'handle': '...', 'nuevo_layer': '...', 'etiqueta': '...'}
    acad_doc: Objeto Document de win32com
    """
    msp = acad_doc.ModelSpace

    # Crear capas necesarias primero (optimización)
    capas_necesarias = set(t["nuevo_layer"] for t in tramos_data)
    for capa in capas_necesarias:
        try:
            acad_doc.Layers.Add(capa)
        except Exception:
            pass  # La capa ya existe

    for tramo in tramos_data:
        try:
            # Obtener objeto por Handle (Mucho más rápido que iterar)
            obj = acad_doc.HandleToObject(tramo["handle"])

            # 1. Cambiar Capa
            if obj.Layer != tramo["nuevo_layer"]:
                obj.Layer = tramo["nuevo_layer"]

            # 2. Crear Etiqueta (MText o Text)
            # Usamos las coordenadas del objeto para centrar el texto
            # Nota: Para polilíneas, obj.Coordinates devuelve lista plana
            if obj.ObjectName == "AcDbPolyline":
                coords = obj.Coordinates
                # Lógica simple para el centro (promedio start/end)
                mid_x = (coords[0] + coords[-2]) / 2
                mid_y = (coords[1] + coords[-1]) / 2

                insert_pnt = win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8, (mid_x, mid_y, 0)
                )
                text_obj = msp.AddText(
                    tramo["etiqueta"], insert_pnt, 1.2
                )  # 1.2 es altura texto
                text_obj.Layer = "ETIQUETAS_AUTO"

        except Exception as e:
            log_warning(f"Error en handle {tramo['handle']}: {e}")
