"""
Lector de bloques avanzado usando win32com
Permite leer atributos y propiedades dinámicas.
"""

from typing import List, Dict, Any
from .acad_interface import get_acad_com


def get_block_attributes(obj: Any) -> Dict[str, str]:
    """Extrae los atributos (Tags/Values) de un bloque."""
    attrs: Dict[str, str] = {}
    try:
        if obj.HasAttributes:
            # GetAttributes devuelve una tupla de objetos
            for att in obj.GetAttributes():
                attrs[att.TagString] = att.TextString
    except Exception:
        pass
    return attrs


def get_dynamic_props(obj: Any) -> Dict[str, Any]:
    """
    Extrae propiedades dinámicas (ej. Visibilidad, Rotación, Flip).
    """
    props: Dict[str, Any] = {}
    try:
        if obj.IsDynamicBlock:
            for prop in obj.GetDynamicBlockProperties():
                props[prop.PropertyName] = prop.Value
    except Exception:
        pass
    return props


def extract_specific_blocks(target_names: List[str]) -> List[Dict[str, Any]]:
    """
    Busca bloques específicos y extrae toda su data.
    Args:
        target_names (list): Lista de nombres de bloques a buscar (ej. ['X_BOX_P']).
    Returns:
        list: Lista de diccionarios con la data encontrada:
        [
            {
                "name": str,
                "handle": str,
                "layer": str,
                "xyz": (x, y, z),
                "attributes": dict,
                "dynamic_props": dict
            }, ...
        ]
    """
    acad = get_acad_com()
    if not acad:
        return []

    doc = acad.ActiveDocument
    msp = doc.ModelSpace
    found_blocks: List[Dict[str, Any]] = []

    # Iteración eficiente sobre ModelSpace
    count = msp.Count
    for i in range(count):
        try:
            item = msp.Item(i)
            # Verificar si es un Bloque (AcDbBlockReference)
            if item.ObjectName == "AcDbBlockReference":
                # Manejo de nombres (incluyendo bloques dinámicos anónimos que empiezan con *U)
                real_name = (
                    item.EffectiveName if hasattr(item, "EffectiveName") else item.Name
                )

                if real_name in target_names:
                    data = {
                        "name": real_name,
                        "handle": item.Handle,
                        "layer": item.Layer,
                        "xyz": item.InsertionPoint,
                        "attributes": get_block_attributes(item),
                        "dynamic_props": get_dynamic_props(item),
                    }
                    found_blocks.append(data)
        except Exception:
            continue

    return found_blocks
