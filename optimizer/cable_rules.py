"""
Lógica de selección automática de cables
Determina el cable ideal basándose en la topología (Origen->Destino) y la longitud.
"""

from typing import Tuple, Optional
from .config_loader import get_config
from .feedback_logger import logger


def obtener_grupo_equipo(nombre_bloque: str) -> str:
    """
    Identifica el rol o grupo de un bloque (ej. 'FAT_INT_3.0_P' -> 'fat_int').
    Usa la sección 'equipos' del config.yaml.
    """
    config_equipos = get_config("equipos", {})
    nombre_bloque = nombre_bloque.upper()

    for grupo, lista_nombres in config_equipos.items():
        if any(nombre_bloque == n.upper() for n in lista_nombres):
            return grupo

    return "desconocido"


def buscar_regla_topologica(nombre_origen: str, nombre_destino: str) -> Optional[str]:
    """
    Busca en el YAML una regla que coincida con el par Origen->Destino.
    Retorna el ID del catálogo de cable a usar (ej. 'mpo_300').
    """
    grupo_origen = obtener_grupo_equipo(nombre_origen)
    grupo_destino = obtener_grupo_equipo(nombre_destino)

    reglas = get_config("reglas_topologia", [])

    for regla in reglas:
        if (
            regla.get("origen_grupo") == grupo_origen
            and regla.get("destino_grupo") == grupo_destino
        ):
            return regla["id_catalogo"]

    return None


def seleccionar_cable(
    longitud: float, nombre_origen: str, nombre_destino: str
) -> Tuple[int, float, str]:
    """
    Algoritmo principal de selección de cable.

    1. Determina el tipo de cable según reglas topológicas.
    2. Busca en el catálogo las longitudes disponibles.
    3. Elige la longitud mínima que cumpla con la reserva requerida.

    Args:
        longitud (float): Distancia real del tramo en metros.
        nombre_origen (str): Nombre del bloque de inicio.
        nombre_destino (str): Nombre del bloque final.

    Returns:
        Tuple[int, float, str]: (LongitudCable, ReservaCalculada, NombreTecnico)
    """
    id_producto = buscar_regla_topologica(nombre_origen, nombre_destino)

    if not id_producto:
        logger.warning(
            f"Regla topológica no encontrada para {nombre_origen}->{nombre_destino}. Usando default."
        )
        id_producto = "distribucion_std"

    config_prod = get_config(f"catalogo_cables.{id_producto}")

    if not config_prod:
        logger.error(f"Configuración de cable '{id_producto}' no encontrada en YAML.")
        raise ValueError(f"Configuracion de cable '{id_producto}' no encontrado.")

    nombre_tecnico = config_prod.get("nombre_tecnico", "UNKNOWN_CABLE")
    disponibles = sorted(config_prod["longitudes"])
    reserva_minima = config_prod.get("reserva_minima", 15)

    # Seleccion matematica
    cable_seleccionado = None
    reserva_calculada = 0

    # Logica de seleccion por longitud y reserva
    for cable in disponibles:
        reserva = cable - longitud
        if reserva >= reserva_minima:
            cable_seleccionado = cable
            reserva_calculada = reserva
            break

    # Fallback si no se encuentra ningún cable que cumpla la reserva mínima
    if cable_seleccionado is None:
        logger.warning(
            f"Longitud {longitud:.2f}m excede cables disponibles en '{id_producto}'. Usando mayor."
        )
        cable_seleccionado = disponibles[-1]
        reserva_calculada = cable_seleccionado - longitud

    logger.debug(
        f"   [RULES] {nombre_origen}->{nombre_destino} ({longitud:.1f}m) => {nombre_tecnico} {cable_seleccionado}m"
    )
    return cable_seleccionado, reserva_calculada, nombre_tecnico
