"""
Optimizador de Fibra Óptica para AutoCAD
"""

from .acad_block_reader import extract_specific_blocks
from .acad_geometry import NetworkGraph
from .cable_rules import seleccionar_cable
from .config_loader import get_config
from .acad_tools import (
    get_acad_com,
    dibujar_debug_offset,
    insertar_etiqueta_inteligente,
)
from .report_generator import exportar_csv
from .topology import detectar_regla_por_topologia, calcular_ruta_completa

__all__ = [
    extract_specific_blocks,
    NetworkGraph,
    seleccionar_cable,
    get_config,
    get_acad_com,
    dibujar_debug_offset,
    insertar_etiqueta_inteligente,
    exportar_csv,
    detectar_regla_por_topologia,
    calcular_ruta_completa,
]
