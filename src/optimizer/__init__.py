"""
Optimizador de Fibra Óptica para AutoCAD
"""

from .autocad_utils import obtener_tramos, obtener_longitud_tramo, get_acad_instance
from .cable_rules import seleccionar_cable, obtener_reserva_requerida
from .logic_cable_assignment import asignar_cables
from .text_labels import etiquetar_tramo
from .report_generator import exportar_csv
from .feedback_logger import log_info, log_warning, log_error
