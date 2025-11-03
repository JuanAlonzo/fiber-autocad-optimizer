"""
Aplica las reglas a cada tramo del dibujo en AutoCAD
"""

from .cable_rules import seleccionar_cable
from .text_labels import etiquetar_tramo
from .feedback_logger import log_error, log_warning, log_info


def asignar_cables(tramos, tipo, acad):
    """
    Asigna cables a los tramos y actualiza el dibujo de AutoCAD.

    Args:
        tramos: Lista de diccionarios con información de tramos
        tipo: Tipo de cable ("xbox_hub", "hub_fat", "expansion")
        acad: Instancia de Autocad

    Returns:
        Lista de resultados procesados
    """
    resultados = []
    errores = 0

    log_info(f"Procesando {len(tramos)} tramo(s) de tipo '{tipo}'")

    for i, tramo in enumerate(tramos, 1):
        try:
            long = tramo["longitud"]
            obj = tramo["obj"]
            handle = tramo["handle"]

            # Determinar cable óptimo
            cable, reserva = seleccionar_cable(long, tipo)
            nueva_capa = f"CABLE PRECONECT {tipo} SM ({cable}M)"

            # Advertir si la reserva es insuficiente
            if reserva < 10:
                log_warning(
                    f"Tramo {handle}: Reserva baja ({reserva:.1f}m < 10m)")
            if reserva < 0:
                log_error(
                    f"Tramo {handle}: Cable insuficiente (reserva negativa: {reserva:.1f}m)")

            capa_cambiada = False
            etiqueta_creada = False

            # Intentar cambiar la capa del objeto
            try:
                obj.Layer = nueva_capa
                capa_cambiada = True
            except Exception as e:
                error_msg = str(e)
                if "Key not found" in error_msg or "-2145386476" in error_msg:
                    log_warning(
                        f"Tramo {handle}: No se pudo cambiar capa - objeto bloqueado o corrupto")
                else:
                    log_warning(
                        f"Tramo {handle}: Error al cambiar capa: {error_msg}")

            # Intentar crear etiqueta de texto
            try:
                texto = f"{tipo.upper()} {cable}M | {round(long, 1)}m | Res: {round(reserva, 1)}m"
                etiquetar_tramo(acad, obj, texto)
                etiqueta_creada = True
            except Exception as e:
                log_warning(f"Tramo {handle}: No se pudo etiquetar - {str(e)}")

            # Registrar resultado (aunque no se haya podido modificar el dibujo)
            resultados.append({
                "handle": handle,
                "capa": nueva_capa if capa_cambiada else tramo.get("layer", "DESCONOCIDA"),
                "longitud": long,
                "reserva": reserva,
                "cable": cable,
                "capa_cambiada": capa_cambiada,
                "etiqueta_creada": etiqueta_creada
            })

            # Mensaje de estado
            estado = []
            if not capa_cambiada:
                estado.append("⚠️ capa no cambiada")
            if not etiqueta_creada:
                estado.append("⚠️ sin etiqueta")

            estado_str = f" ({', '.join(estado)})" if estado else ""
            log_info(
                f"Tramo {i}/{len(tramos)}: {handle} → {cable}m (Res: {reserva:.1f}m){estado_str}")

        except Exception as e:
            errores += 1
            log_error(
                f"Error general procesando tramo {tramo.get('handle', 'DESCONOCIDO')}: {e}")
            continue

    log_info(
        f"Proceso completado: {len(resultados)} exitosos, {errores} con errores")

    return resultados
