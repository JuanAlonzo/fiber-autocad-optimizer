"""
Optimizador de Fibra Óptica para AutoCAD
"""

from .acad_block_reader import extract_specific_blocks
from .acad_geometry import NetworkGraph
from .acad_utils import obtener_tramos, obtener_bloques, get_acad_instance
from .cable_rules import seleccionar_cable, obtener_reserva_requerida
from .feedback_logger import log_info, log_warning, log_error
from .logic_cable_assignment import asignar_cables
from .report_generator import exportar_csv
from .topology import detectar_regla_por_topologia

__all__ = [
    NetworkGraph,
    extract_specific_blocks,
    obtener_tramos,
    obtener_bloques,
    get_acad_instance,
    seleccionar_cable,
    obtener_reserva_requerida,
    log_info,
    log_warning,
    log_error,
    asignar_cables,
    exportar_csv,
    detectar_regla_por_topologia,
]
