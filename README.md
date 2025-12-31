# 📔 Analizador de Diario Personal

Herramienta automatizada para analizar entradas de diario personal usando modelos de lenguaje locales (LM Studio). Procesa carpetas completas de diarios, extrae información estructurada como emociones, temas, personas mencionadas y genera resúmenes neutrales.

## ✨ Características

- 🤖 **Análisis con IA Local**: Utiliza LM Studio para procesamiento privado
- 📁 **Procesamiento Batch**: Analiza carpetas completas automáticamente
- 🔍 **Detección Inteligente**: Solo procesa archivos nuevos, evita duplicados
- 📊 **Extracción Estructurada**: Genera JSON con emociones, temas y resúmenes
- 📅 **Gestión Automática de Fechas**: Extrae y valida fechas del nombre del archivo
- 🛡️ **Manejo Robusto de Errores**: Validación completa y mensajes claros
- 📝 **Logging Detallado**: Seguimiento completo del proceso con estadísticas
- 💾 **Historial Acumulativo**: Mantiene registro de todos los análisis
- 🔒 **Privacidad Total**: Todo el procesamiento es local

## 📋 Requisitos Previos

### Software Necesario

- **Python 3.7 o superior**
- **LM Studio** instalado y en ejecución
  - Descarga desde: [lmstudio.ai](https://lmstudio.ai)
  - Debe estar corriendo el servidor local

### Dependencias Python

```bash
pip install lmstudio
```

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/tu-usuario/diary-analyzer.git
cd diary-analyzer
```

### 2. Crear entorno virtual (recomendado)

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
# En Linux/Mac:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install lmstudio
```

### 4. Crear estructura de carpetas

```bash
mkdir diarios
```

### 5. Configurar LM Studio

1. Abre LM Studio
2. Descarga el modelo: `liquidai/lfm2-2.6b-exp@f16` (o el que prefieras)
3. Inicia el servidor local (generalmente en `http://localhost:1234`)

## 📖 Uso

### Uso Básico (Procesamiento Batch)

1. **Coloca tus archivos de diario** en la carpeta `diarios/` con el formato `dd-mm-yyyy.md`:

```
diarios/
├── 01-12-2025.md
├── 15-12-2025.md
├── 20-12-2025.md
└── 31-12-2025.md
```

2. **Ejecuta el script**:

```bash
python diary_analyzer.py
```

3. **Resultado**: El script procesará todos los archivos nuevos y generará/actualizará `diario.json`

### Ejemplo de Salida

```
============================================================
INICIANDO PROCESAMIENTO BATCH DE DIARIOS
============================================================
Encontrados 4 archivos de diario en 'diarios'
Encontradas 2 entradas ya procesadas
Archivos pendientes de procesar: 2
Modo: SOLO NUEVOS
Archivos a procesar: 2
------------------------------------------------------------

[1/2] Procesando...
2025-12-31 10:15:23 - INFO - Analizando: 20-12-2025.md (20-12-2025)
2025-12-31 10:15:25 - INFO - ✓ 20-12-2025.md procesado exitosamente
Esperando 1 segundo antes del siguiente archivo...

[2/2] Procesando...
2025-12-31 10:15:26 - INFO - Analizando: 31-12-2025.md (31-12-2025)
2025-12-31 10:15:28 - INFO - ✓ 31-12-2025.md procesado exitosamente

============================================================
RESUMEN DEL PROCESAMIENTO
============================================================
Total de archivos: 2
✓ Exitosos: 2
✗ Fallidos: 0
⊘ Omitidos: 0

🎉 ¡Todos los archivos procesados exitosamente!
============================================================
✓ Procesamiento completado: 2 archivos analizados
============================================================
```

### Configuración Personalizada

Edita las constantes al final de `diary_analyzer.py`:

```python
if __name__ == "__main__":
    CARPETA_DIARIOS = "mis_diarios"      # Tu carpeta personalizada
    ARCHIVO_SALIDA = "analisis.json"     # Archivo de salida
    MODELO_LLM = "mistral-7b-instruct"   # Modelo diferente
    FORZAR_REPROCESAR = False            # True para reprocesar todo
```

### Reprocesar Todos los Archivos

Si quieres volver a analizar todos los archivos (incluso los ya procesados):

```python
FORZAR_REPROCESAR = True
```

### Uso como Módulo

```python
from diary_analyzer import procesar_carpeta_diarios

# Procesar carpeta completa
estadisticas = procesar_carpeta_diarios(
    carpeta="diarios",
    ruta_salida="resultados.json",
    modelo="liquidai/lfm2-2.6b-exp@f16",
    forzar_reprocesar=False
)

print(f"Procesados: {estadisticas['exitosos']}")
print(f"Fallidos: {estadisticas['fallidos']}")
```

### Uso de Funciones Individuales

```python
from diary_analyzer import (
    obtener_archivos_diario,
    obtener_archivos_pendientes,
    analizar_diario_individual
)

# Ver qué archivos hay
archivos = obtener_archivos_diario("diarios")
print(f"Total de archivos: {len(archivos)}")

# Ver cuáles faltan por procesar
pendientes = obtener_archivos_pendientes("diarios", "diario.json")
print(f"Pendientes: {len(pendientes)}")

# Procesar uno específico
from pathlib import Path
archivo = Path("diarios/15-12-2025.md")
resultado = analizar_diario_individual(archivo)
```

## 📄 Formato de Archivos

### Nombre de Archivo (IMPORTANTE)

Los archivos **DEBEN** seguir el formato: `dd-mm-yyyy.md`

✅ **Válidos:**
- `01-12-2025.md`
- `15-01-2024.md`
- `31-12-2025.md`

❌ **Inválidos:**
- `2025-12-01.md` (formato incorrecto)
- `1-12-2025.md` (día sin cero)
- `diario.md` (sin fecha)
- `15-12-25.md` (año incompleto)

### Contenido del Archivo

Texto libre en formato Markdown:

```markdown
# 15 de Diciembre, 2025

Hoy fue un día interesante. Me reuní con María para discutir el proyecto.
Me sentí un poco ansioso al principio, pero luego todo fluyó naturalmente.

Aprendí mucho sobre React y estoy emocionado por implementarlo.
También hablé con Juan sobre sus planes de viaje.

## Reflexiones

El día fue productivo. Necesito seguir trabajando en mi confianza.
```

## 📊 Formato de Salida

El análisis se guarda en formato JSON con la siguiente estructura:

```json
[
  {
    "fecha": "15-12-2025",
    "summary": "Reunión productiva sobre proyecto con María. Aprendizaje de React y conversación con Juan sobre viajes.",
    "emotions": ["ansioso", "emocionado"],
    "topics": ["trabajo", "programación", "viajes", "confianza"],
    "people": ["María", "Juan"],
    "intensity": "media"
  },
  {
    "fecha": "20-12-2025",
    "summary": "...",
    "emotions": ["feliz", "relajado"],
    "topics": ["familia", "descanso"],
    "people": null,
    "intensity": "baja"
  }
]
```

### Campos del Análisis

- **fecha**: Fecha del diario en formato `dd-mm-yyyy` (extraída del nombre del archivo)
- **summary**: Resumen neutral en máximo 3 líneas
- **emotions**: Lista de emociones detectadas (puede ser lista vacía)
- **topics**: Temas principales discutidos
- **people**: Personas mencionadas (null si no hay ninguna)
- **intensity**: Intensidad emocional ("baja", "media" o "alta")

## 🔧 Configuración Avanzada

### Cambiar el Modelo

Puedes usar cualquier modelo compatible con LM Studio:

```python
MODELO_LLM = "mistral-7b-instruct"
# o
MODELO_LLM = "llama-2-7b-chat"
# o
MODELO_LLM = "phi-2"
```

### Ajustar el Logging

Modifica el nivel de logging al inicio del script:

```python
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Cambiar Tiempo de Espera Entre Archivos

En la función `procesar_carpeta_diarios`, busca:

```python
time.sleep(1)  # Cambiar a 2, 3, etc.
```

## 🐛 Solución de Problemas

### Error: "La carpeta 'diarios' no existe"

**Solución**: 
```bash
mkdir diarios
```

### Error: "No se encontraron archivos de diario válidos"

**Causas posibles**:
- Los archivos no siguen el formato `dd-mm-yyyy.md`
- La carpeta está vacía
- Los archivos no tienen extensión `.md`

**Solución**:
```bash
# Renombrar archivos al formato correcto
mv diario-2025-12-15.md 15-12-2025.md
```

### Error: "No se pudo conectar con LM Studio"

**Solución**: 
- Verifica que LM Studio esté abierto
- Confirma que el servidor local esté activo
- Revisa que el puerto sea el correcto (por defecto 1234)

### Archivos ya procesados no se detectan

**Causa**: El campo `fecha` no existe en el JSON

**Solución**:
```python
# Forzar reprocesamiento
FORZAR_REPROCESAR = True
```

### Error: "Fecha inválida"

**Causa**: El nombre del archivo tiene una fecha imposible (ej: `32-13-2025.md`)

**Solución**: Corrige el nombre del archivo a una fecha válida

### Algunos archivos fallan pero otros no

**Comportamiento normal**: El script continúa procesando aunque algunos fallen

**Revisa los logs** para ver qué archivos fallaron y por qué

## 📁 Estructura del Proyecto

```
diary-analyzer/
├── diary_analyzer.py      # Script principal
├── README.md              # Esta documentación
├── .venv/                 # Entorno virtual (opcional)
├── diarios/              # Carpeta con tus archivos .md
│   ├── 01-12-2025.md
│   ├── 15-12-2025.md
│   └── 31-12-2025.md
└── diario.json           # Historial de análisis (generado)
```

## 🔒 Privacidad y Seguridad

- ✅ Todo el procesamiento es **100% local**
- ✅ No se envían datos a servicios externos
- ✅ Tus diarios permanecen en tu computadora
- ✅ Sin conexión a internet requerida (excepto instalación inicial)
- ✅ El historial se guarda solo en tu máquina

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Ejemplos de Uso Avanzado

### Obtener Estadísticas del Historial

```python
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

# Cargar historial
data = json.loads(Path("diario.json").read_text())

# Emociones más comunes
todas_emociones = []
for entrada in data:
    todas_emociones.extend(entrada.get("emotions", []))

contador = Counter(todas_emociones)
print("Emociones más frecuentes:")
for emocion, count in contador.most_common(5):
    print(f"  {emocion}: {count}")

# Intensidad promedio
intensidades = {"baja": 1, "media": 2, "alta": 3}
total = sum(intensidades.get(e.get("intensity", "media"), 2) for e in data)
promedio = total / len(data) if data else 0
print(f"\nIntensidad emocional promedio: {promedio:.2f}/3")

# Días analizados
print(f"\nTotal de días analizados: {len(data)}")
```

### Filtrar por Fecha

```python
from datetime import datetime

def filtrar_por_mes(historial, mes, anio):
    """Filtra entradas de un mes específico"""
    resultado = []
    for entrada in historial:
        fecha = datetime.strptime(entrada['fecha'], '%d-%m-%Y')
        if fecha.month == mes and fecha.year == anio:
            resultado.append(entrada)
    return resultado

# Cargar historial
data = json.loads(Path("diario.json").read_text())

# Ver diciembre 2025
diciembre = filtrar_por_mes(data, 12, 2025)
print(f"Entradas en diciembre 2025: {len(diciembre)}")
```

### Buscar por Persona

```python
def buscar_menciones_persona(historial, nombre):
    """Encuentra todas las entradas donde se menciona a una persona"""
    resultado = []
    for entrada in historial:
        personas = entrada.get('people', [])
        if personas and nombre in personas:
            resultado.append({
                'fecha': entrada['fecha'],
                'summary': entrada['summary']
            })
    return resultado

# Buscar menciones de María
menciones = buscar_menciones_persona(data, "María")
print(f"María fue mencionada {len(menciones)} veces")
for mencion in menciones:
    print(f"  {mencion['fecha']}: {mencion['summary'][:50]}...")
```

### Exportar a CSV

```python
import csv

def exportar_a_csv(historial, nombre_archivo="diario.csv"):
    """Exporta el historial a formato CSV"""
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
        campos = ['fecha', 'summary', 'emotions', 'topics', 'people', 'intensity']
        writer = csv.DictWriter(f, fieldnames=campos)
        
        writer.writeheader()
        for entrada in historial:
            # Convertir listas a strings
            row = entrada.copy()
            if row.get('emotions'):
                row['emotions'] = ', '.join(row['emotions'])
            if row.get('topics'):
                row['topics'] = ', '.join(row['topics'])
            if row.get('people'):
                row['people'] = ', '.join(row['people'])
            writer.writerow(row)

# Usar
data = json.loads(Path("diario.json").read_text())
exportar_a_csv(data)
print("Exportado a diario.csv")
```

### Procesar Solo Archivos de un Mes

```python
from pathlib import Path
from datetime import datetime

def procesar_mes_especifico(carpeta, mes, anio):
    """Procesa solo archivos de un mes específico"""
    archivos = obtener_archivos_diario(carpeta)
    
    archivos_filtrados = []
    for archivo in archivos:
        fecha_str = extraer_fecha_de_nombre(archivo.name)
        if fecha_str:
            fecha = datetime.strptime(fecha_str, '%d-%m-%Y')
            if fecha.month == mes and fecha.year == anio:
                archivos_filtrados.append(archivo)
    
    print(f"Procesando {len(archivos_filtrados)} archivos de {mes}/{anio}")
    
    for archivo in archivos_filtrados:
        analizar_diario_individual(archivo)

# Procesar solo diciembre 2025
procesar_mes_especifico("diarios", 12, 2025)
```

## 🗺️ Roadmap

- [ ] Interfaz gráfica (GUI)
- [ ] Dashboard web con visualizaciones
- [ ] Gráficos de emociones a lo largo del tiempo
- [ ] Exportación a PDF/HTML/CSV
- [ ] Búsqueda avanzada (por fecha/emoción/persona/tema)
- [ ] Detección de patrones y tendencias
- [ ] Notificaciones para recordar escribir
- [ ] Soporte para múltiples idiomas
- [ ] Integración con Obsidian/Notion
- [ ] Tests unitarios completos
- [ ] API REST opcional
- [ ] Sincronización entre dispositivos (opcional)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

**Fabri**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- [LM Studio](https://lmstudio.ai) por proporcionar una excelente plataforma local
- [Liquid AI](https://liquid.ai) por el modelo LFM
- La comunidad de código abierto

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Busca en [Issues](https://github.com/tu-usuario/diary-analyzer/issues)
3. Abre un nuevo issue con detalles específicos:
   - Versión de Python
   - Sistema operativo
   - Mensaje de error completo
   - Logs relevantes

## 🔄 Changelog

### v2.0.0 (2025-01-01)
- ✨ Procesamiento batch de carpetas completas
- ✨ Detección automática de archivos ya procesados
- ✨ Extracción y validación de fechas desde nombres de archivo
- ✨ Sistema de estadísticas y resumen
- ✨ Validación de formato de nombres de archivo
- 🐛 Mejoras en manejo de errores
- 📝 Logging más detallado

### v1.0.0 (2024-12-15)
- 🎉 Versión inicial
- ✨ Análisis individual de archivos
- ✨ Integración con LM Studio
- ✨ Extracción de emociones, temas y personas

---

**¿Te resultó útil este proyecto? ¡Dale una ⭐ en GitHub!**