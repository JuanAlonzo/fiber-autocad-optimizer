# 🔧 Scripts de Cambio de Capa - Guía de Uso

## 📁 Scripts Disponibles

### 1️⃣ **cambiar_capa.py** - Cambio Simple
Script básico para cambiar la capa de todos los tramos a una capa específica.

**Uso:**
```bash
python test/cambiar_capa.py
```

**Características:**
- ✅ Cambio directo a `CABLE PRECONECT 2H SM (150M)`
- ✅ Muestra progreso en tiempo real
- ✅ Manejo de errores robusto
- ✅ Resumen final de operación

**Salida esperada:**
```
=== SCRIPT DE CAMBIO DE CAPA ===
Nueva capa: CABLE PRECONECT 2H SM (150M)

INFO: Se encontraron 15 tramo(s)
INFO: ✅ Tramo 1/15: 3365 | TRAMO_ORIGINAL → CABLE PRECONECT 2H SM (150M) | 245.5m
INFO: ✅ Tramo 2/15: 3366 | TRAMO_ORIGINAL → CABLE PRECONECT 2H SM (150M) | 155.2m
ERROR: ❌ Tramo 3/15: 3368 | Objeto bloqueado o corrupto
...

==================================================
RESUMEN:
  ✅ Exitosos: 14
  ❌ Errores: 1
  📊 Total: 15
==================================================
```

---

### 2️⃣ **cambiar_capa_interactivo.py** - Cambio Interactivo
Script avanzado con menú de selección y confirmación.

**Uso:**
```bash
python test/cambiar_capa_interactivo.py
```

**Características:**
- ✅ Menú interactivo de capas predefinidas
- ✅ Opción de capa personalizada
- ✅ Confirmación antes de cambiar
- ✅ Resumen detallado de errores
- ✅ Sugerencias de corrección

**Flujo de uso:**
```
============================================================
  CAMBIO DE CAPA DE TRAMOS - SELECTOR INTERACTIVO
============================================================

Selecciona la nueva capa:
  1. CABLE PRECONECT 2H SM (150M)
  2. CABLE PRECONECT 2H SM (200M)
  3. CABLE PRECONECT 2H SM (300M)
  4. CABLE PRECONECT 2H SM (100M)
  5. CABLE PRECONECT 2H SM (50M)
  0. CAPA PERSONALIZADA
============================================================

Selecciona una opción: 1

============================================================
⚠️  CONFIRMACIÓN DE CAMBIOS
============================================================
  Tramos encontrados: 15
  Nueva capa: CABLE PRECONECT 2H SM (150M)

  Capas actuales a modificar:
    • TRAMO_ORIGINAL (12 tramo(s))
    • TRAMO_SECUNDARIO (3 tramo(s))
============================================================

¿Deseas continuar? (s/n): s

🔧 Cambiando capas...
============================================================
✅ [1/15] 3365 | 245.5m | TRAMO_ORIGINAL... → CABLE PRECONECT 2H SM (150M)...
✅ [2/15] 3366 | 155.2m | TRAMO_ORIGINAL... → CABLE PRECONECT 2H SM (150M)...
...
```

---

### 3️⃣ **diagnostico_estado_tramos.py** - Diagnóstico
Script para verificar el estado de los tramos antes de cambiarlos.

**Uso General:**
```bash
python test/diagnostico_estado_tramos.py
```

**Uso para Tramo Específico:**
```bash
python test/diagnostico_estado_tramos.py 3368
```

**Características:**
- ✅ Verifica si se puede cambiar la capa
- ✅ Verifica si se puede leer BoundingBox (para etiquetas)
- ✅ Detecta objetos bloqueados
- ✅ Muestra tabla resumen
- ✅ Recomendaciones automáticas

**Salida esperada:**
```
======================================================================
  🔍 DIAGNÓSTICO DE ESTADO DE TRAMOS
======================================================================
✅ Se encontraron 15 tramo(s)

#    Handle   Longitud   Capa         BBox   Lock   Estado
----------------------------------------------------------------------
1    3365     245.5      TRAMO_ORIGI  ✓      ✗      ✅ OK
2    3366     155.2      TRAMO_ORIGI  ✓      ✗      ✅ OK
3    3368     245.5      TRAMO_ORIGI  ✗      ✗      ⚠️  Sin BBox
4    3369     155.8      TRAMO_ORIGI  ✓      ✗      ✅ OK
...

======================================================================
📊 RESUMEN DEL DIAGNÓSTICO
======================================================================
  Total de tramos: 15

  Cambio de capa:
    ✅ Pueden cambiar capa: 15
    ❌ NO pueden cambiar capa: 0

  BoundingBox (para etiquetas):
    ✅ Pueden leer BoundingBox: 14
    ❌ NO pueden leer BoundingBox: 1

  Estado de bloqueo:
    🔒 Objetos bloqueados: 0
======================================================================

💡 RECOMENDACIONES:
  • Ejecuta AUDIT en AutoCAD para corregir objetos
  • Algunos objetos pueden estar corruptos
======================================================================
```

---

## 🎯 Flujo de Trabajo Recomendado

### **Paso 1: Diagnóstico**
Antes de cambiar capas, ejecuta el diagnóstico:
```bash
python test/diagnostico_estado_tramos.py
```

Esto te dirá:
- ✅ Cuántos tramos se pueden modificar
- ⚠️ Cuáles tienen problemas
- 💡 Qué hacer para corregir errores

### **Paso 2: Corrección (si es necesario)**
Si el diagnóstico muestra errores, ejecuta en AutoCAD:
```
AUDIT          # Corrige objetos corruptos
PURGE          # Limpia objetos no usados
```

Desbloquea capas:
```
Comando: LAYER
→ Selecciona todas las capas
→ Click en el icono de candado para desbloquear
```

### **Paso 3: Cambio de Capa**
Ejecuta el script interactivo:
```bash
python test/cambiar_capa_interactivo.py
```

O el script simple si sabes la capa exacta:
```bash
python test/cambiar_capa.py
```

---

## 📝 Personalización

### **Cambiar la capa predeterminada en `cambiar_capa.py`:**

Edita la línea:
```python
def cambiar_capa_tramos(nueva_capa="CABLE PRECONECT 2H SM (150M)"):
```

Cambia `"CABLE PRECONECT 2H SM (150M)"` por la capa que desees.

### **Agregar más capas al menú interactivo:**

Edita el diccionario en `cambiar_capa_interactivo.py`:
```python
CAPAS_DISPONIBLES = {
    "1": "CABLE PRECONECT 2H SM (150M)",
    "2": "CABLE PRECONECT 2H SM (200M)",
    "3": "CABLE PRECONECT 2H SM (300M)",
    "4": "CABLE PRECONECT 2H SM (100M)",
    "5": "CABLE PRECONECT 2H SM (50M)",
    "6": "TU_CAPA_PERSONALIZADA",  # ← Agregar aquí
}
```

---

## 🔍 Casos de Uso

### **Caso 1: Cambio masivo a capa específica**
```bash
# Cambiar todos los tramos a 150M
python test/cambiar_capa.py
```

### **Caso 2: Seleccionar capa del menú**
```bash
# Usar menú interactivo
python test/cambiar_capa_interactivo.py
# Seleccionar opción 2 → CABLE PRECONECT 2H SM (200M)
```

### **Caso 3: Capa personalizada**
```bash
# Usar menú interactivo
python test/cambiar_capa_interactivo.py
# Seleccionar opción 0 → Ingresar: MI_CAPA_CUSTOM
```

### **Caso 4: Verificar estado antes de cambiar**
```bash
# Ejecutar diagnóstico primero
python test/diagnostico_estado_tramos.py

# Si todo está OK, proceder con el cambio
python test/cambiar_capa_interactivo.py
```

### **Caso 5: Diagnosticar un tramo problemático**
```bash
# Si el tramo 3368 da error
python test/diagnostico_estado_tramos.py 3368

# Verás pruebas detalladas:
# - ✅ Puede leer Layer
# - ✅ Puede leer Length
# - ❌ NO puede leer BoundingBox → No se puede etiquetar
# - ✅ Puede cambiar capa
```

---

## 🛠️ Integración con el Optimizador

Estos scripts usan las mismas funciones que `main.py`:

```python
from optimizer import (
    obtener_tramos,      # ← Obtiene polilíneas con "TRAMO" en la capa
    log_info,            # ← Logging informativo
    log_warning,         # ← Logging de advertencias
    log_error            # ← Logging de errores
)
```

**Ventajas:**
- ✅ Mismo manejo de errores que el optimizador principal
- ✅ Logs consistentes en `logs/proceso.log`
- ✅ Misma lógica de detección de tramos
- ✅ Compatibilidad total con el flujo de trabajo

---

## ⚠️ Errores Comunes

### **Error: "No se encontraron tramos"**
**Causa:** No hay polilíneas con "TRAMO" en el nombre de capa.

**Solución:**
```python
# Verifica en AutoCAD que las polilíneas tengan:
# - ObjectName: AcDbPolyline
# - Layer: Debe contener "TRAMO" (ej: TRAMO_ORIGINAL, TRAMO_1, etc.)
```

### **Error: "Objeto bloqueado o corrupto"**
**Causa:** El objeto no permite cambiar la capa.

**Solución:**
```
1. En AutoCAD: LAYER → Desbloquear todas
2. En AutoCAD: AUDIT → Fix
3. Verificar que no haya XREF bloqueadas
```

### **Error: "Key not found" (-2145386476)**
**Causa:** Propiedad de AutoCAD inaccesible.

**Solución:**
```
1. AUDIT en AutoCAD
2. Guardar y reabrir el dibujo
3. Si persiste, el objeto puede estar corrupto → Eliminar y recrear
```

---

## 📊 Comparación de Scripts

| Característica | cambiar_capa.py | cambiar_capa_interactivo.py | diagnostico_estado_tramos.py |
|----------------|-----------------|------------------------------|------------------------------|
| **Interactivo** | ❌ No | ✅ Sí | ✅ Sí |
| **Menú de capas** | ❌ No | ✅ Sí | N/A |
| **Confirmación** | ❌ No | ✅ Sí | N/A |
| **Capa personalizada** | ⚠️ Manual | ✅ Automático | N/A |
| **Diagnóstico** | ❌ No | ⚠️ Básico | ✅ Completo |
| **Velocidad** | 🚀 Rápido | ⚙️ Moderado | 🔍 Lento |
| **Uso recomendado** | Scripts automáticos | Uso manual | Troubleshooting |

---

## 🎓 Ejemplo Completo

```bash
# 1. Diagnosticar estado actual
python test/diagnostico_estado_tramos.py

# Salida:
# ✅ Se encontraron 15 tramo(s)
# ✅ Pueden cambiar capa: 15
# ❌ NO pueden leer BoundingBox: 1
# 💡 RECOMENDACIONES: Ejecuta AUDIT

# 2. Corregir en AutoCAD
# Comando: AUDIT

# 3. Verificar nuevamente
python test/diagnostico_estado_tramos.py

# Salida:
# ✅ TODOS LOS TRAMOS ESTÁN EN BUEN ESTADO

# 4. Cambiar capas
python test/cambiar_capa_interactivo.py

# Menú → Seleccionar opción 1 (150M)
# Confirmar → s
# Resultado: ✅ 15 exitosos, 0 errores
```

---

**Fecha**: 14 de octubre de 2025  
**Versión**: 1.0  
**Estado**: ✅ LISTO PARA USO

---

## 💡 Tips Avanzados

### **Usar desde Python (sin ejecutar script):**
```python
from test.cambiar_capa_interactivo import cambiar_capa_sin_confirmacion

# Cambiar a 200M sin interacción
exitosos, errores = cambiar_capa_sin_confirmacion("CABLE PRECONECT 2H SM (200M)")
print(f"Exitosos: {exitosos}, Errores: {errores}")
```

### **Filtrar tramos específicos:**
```python
from optimizer import obtener_tramos

tramos = obtener_tramos()

# Solo tramos largos (>200m)
tramos_largos = [t for t in tramos if t["longitud"] > 200]

# Cambiar solo esos
for t in tramos_largos:
    t["obj"].Layer = "CABLE PRECONECT 2H SM (300M)"
```

### **Logging personalizado:**
Los scripts usan el sistema de logging del optimizador. Los logs se guardan en:
```
logs/proceso.log
```

Para ver los logs en tiempo real:
```bash
tail -f logs/proceso.log
```
