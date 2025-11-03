"""
Script de prueba para cambiar capa de polilíneas TRAMO
"""
from pyautocad import Autocad
from optimizer import obtener_tramos, log_info, log_warning, log_error

acad = Autocad(create_if_not_exists=True)

def cambiar_capa_tramos(nueva_capa="CABLE PRECONECT 2H SM (150M)"):
    """
    Cambia la capa de todos los tramos encontrados a una nueva capa.
    
    Args:
        nueva_capa: Nombre de la nueva capa a asignar
    """
    print("\n=== SCRIPT DE CAMBIO DE CAPA ===")
    print(f"Nueva capa: {nueva_capa}\n")
    
    # Obtener todos los tramos usando la función del optimizador
    tramos = obtener_tramos()
    
    if not tramos:
        log_warning("No se encontraron tramos con 'TRAMO' en el nombre de capa")
        return
    
    log_info(f"Se encontraron {len(tramos)} tramo(s)")
    
    exitosos = 0
    errores = 0
    
    # Intentar cambiar la capa de cada tramo
    for i, tramo in enumerate(tramos, 1):
        handle = tramo["handle"]
        capa_original = tramo["layer"]
        longitud = tramo["longitud"]
        obj = tramo["obj"]
        
        try:
            # Intentar cambiar la capa
            obj.Layer = nueva_capa
            exitosos += 1
            log_info(f"✅ Tramo {i}/{len(tramos)}: {handle} | {capa_original} → {nueva_capa} | {longitud:.1f}m")
            
        except Exception as e:
            errores += 1
            error_msg = str(e)
            
            # Detectar tipo de error
            if "Key not found" in error_msg or "-2145386476" in error_msg:
                log_error(f"❌ Tramo {i}/{len(tramos)}: {handle} | Objeto bloqueado o corrupto")
            else:
                log_error(f"❌ Tramo {i}/{len(tramos)}: {handle} | {error_msg}")
    
    # Resumen
    print("\n" + "="*50)
    print(f"RESUMEN:")
    print(f"  ✅ Exitosos: {exitosos}")
    print(f"  ❌ Errores: {errores}")
    print(f"  📊 Total: {len(tramos)}")
    print("="*50)
    
    return exitosos, errores

if __name__ == "__main__":
    # Ejecutar el cambio de capa
    cambiar_capa_tramos()
