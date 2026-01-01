# 🧠 Diario Reflexivo con IA

> Sistema completo de análisis semántico de diario personal con RAG (Retrieval Augmented Generation), búsqueda vectorial y chatbot conversacional local.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](CHANGELOG.md)

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características](#-características)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Guía de Uso](#-guía-de-uso)
- [Formato de Archivos](#-formato-de-archivos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Configuración Avanzada](#-configuración-avanzada)
- [Solución de Problemas](#-solución-de-problemas)
- [Roadmap](#-roadmap)
- [Contribuir](#-contribuir)
- [Privacidad](#-privacidad)
- [Licencia](#-licencia)

---

## 🎯 Descripción General

**Diario Reflexivo con IA** es un sistema integral que transforma tus entradas de diario personal en una base de conocimiento semántica consultable. Utiliza modelos de lenguaje locales (LM Studio) para análisis, embeddings multilingües para búsqueda semántica, y RAG para conversaciones contextualizadas con tus propias reflexiones.

### ¿Qué hace este sistema?

1. **Analiza** automáticamente tus entradas de diario (emociones, temas, personas)
2. **Divide** el texto en chunks semánticos coherentes
3. **Genera** embeddings vectoriales para búsqueda por similitud
4. **Indexa** todo en FAISS para recuperación eficiente
5. **Permite** conversar con tus memorias mediante un chatbot inteligente

### ¿Por qué usar este sistema?

- ✅ **100% privado y local** - Ningún dato sale de tu computadora
- ✅ **Búsqueda semántica** - Encuentra entradas por significado, no solo palabras
- ✅ **Chatbot reflexivo** - Conversa con tus propias experiencias pasadas
- ✅ **Análisis estructurado** - Detecta patrones emocionales y temáticos
- ✅ **Modular y extensible** - Arquitectura clara con componentes independientes

---

## ✨ Características

### 📝 Análisis de Diario (`diary_analyzer.py`)

- **Procesamiento batch** de carpetas completas
- **Extracción estructurada** con IA:
  - Resúmenes neutrales
  - Emociones detectadas
  - Temas principales
  - Personas mencionadas
  - Intensidad emocional
- **Chunking semántico inteligente**:
  - División por coherencia narrativa (100-300 palabras)
  - Clasificación automática (hechos/emociones/reflexión/mixto)
  - Metadata enriquecida por chunk
- **Gestión incremental** - Solo procesa archivos nuevos
- **Validación robusta** de formatos y fechas

### 🔍 Motor de Búsqueda Semántica (`query_engine.py`)

- **Embeddings multilingües** (intfloat/multilingual-e5-small)
- **Índice FAISS** optimizado (IndexFlatIP)
- **Búsqueda por similitud** semántica
- **Construcción de contexto** relevante para RAG
- **Metadata persistente** separada de vectores

### 💬 Chatbot RAG (`rag_chat_engine.py`)

- **Conversaciones contextualizadas** con tu diario
- **Prompt especializado** para reflexión personal
- **Integración con LM Studio** (modelos 7B-14B locales)
- **Recuperación automática** de entradas relevantes
- **Respuestas empáticas** basadas en tu historial

### 🎨 Interfaz Web (`app.py`)

- **UI limpia** con Streamlit
- **Chat interactivo** en tiempo real
- **Visualización** de contexto recuperado
- **Historial** de conversación persistente

---

## 🏗️ Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                     FLUJO DE DATOS                            │
└──────────────────────────────────────────────────────────────┘

  📁 diarios/*.md
       │
       ▼
  ┌─────────────────────┐
  │ diary_analyzer.py   │ ← LM Studio (2.6B-7B)
  │                     │   • Análisis de emociones
  │                     │   • Chunking semántico
  └──────┬──────────────┘
         │
         ├──► 📄 diario.json (análisis completo)
         │
         └──► 📄 diario_chunks.json (chunks)
                      │
                      ▼
         ┌─────────────────────────┐
         │ embedding_generator.py  │ ← Sentence Transformers
         │                         │   • multilingual-e5-small
         └──────┬──────────────────┘
                │
                ├──► 🗂️ diario_index.faiss (vectores)
                │
                └──► 📄 diario_metadata.json (texto + info)
                           │
                           ▼
              ┌──────────────────────┐
              │   query_engine.py    │ ← FAISS Search
              │                      │   • Búsqueda semántica
              └──────┬───────────────┘
                     │
                     ▼
              ┌──────────────────────┐
              │  rag_chat_engine.py  │ ← LM Studio (7B-14B)
              │                      │   • RAG + Reflexión
              └──────┬───────────────┘
                     │
                     ▼
              ┌──────────────────────┐
              │      app.py          │ ← Streamlit
              │   (Interfaz Web)     │
              └──────────────────────┘
```

### Componentes Principales

| Componente | Responsabilidad | Tecnología |
|------------|----------------|------------|
| `diary_analyzer.py` | Análisis de texto y chunking | LM Studio (LLM 2.6B-7B) |
| `embedding_generator.py` | Generación de embeddings | Sentence Transformers |
| `query_engine.py` | Búsqueda semántica | FAISS + NumPy |
| `rag_chat_engine.py` | Chatbot RAG | LM Studio + Requests |
| `app.py` | Interfaz de usuario | Streamlit |

---

## 📋 Requisitos

### Software Necesario

- **Python 3.7+** ([Descargar](https://www.python.org/downloads/))
- **LM Studio** ([Descargar](https://lmstudio.ai))
  - Servidor local corriendo en `http://localhost:1234`
  - Modelos recomendados:
    - Análisis: `liquidai/lfm2-2.6b-exp` o `Qwen2.5-7B-Instruct`
    - Chat: `Qwen2.5-7B-Instruct` o `Llama-3.1-8B-Instruct`

### Dependencias Python

```txt
# Core
streamlit==1.52.2
requests==2.32.5
numpy==2.4.0

# Embeddings y búsqueda
sentence-transformers==5.2.0
faiss-cpu==1.13.2
torch==2.9.1

# Análisis de diario
lmstudio==1.5.0
```

### Requisitos de Hardware

- **RAM**: Mínimo 8GB, recomendado 16GB
- **Disco**: ~5GB para modelos + datos
- **CPU**: Cualquier procesador moderno (GPU opcional para mayor velocidad)

---

## 🚀 Instalación

### Opción 1: Instalación Rápida (Script Automático)

```bash
# 1. Clonar el repositorio
git clone https://github.com/fabricioarce/diary-analyzer.git
cd diary-analyzer

# 2. Ejecutar script de instalación
chmod +x run.sh
./run.sh
```

El script automáticamente:
- ✅ Crea el entorno virtual
- ✅ Instala dependencias
- ✅ Configura carpetas necesarias
- ✅ Ejecuta el pipeline completo

### Opción 2: Instalación Manual

#### Paso 1: Preparar el Entorno

```bash
# Clonar repositorio
git clone https://github.com/fabricioarce/diary-analyzer.git
cd diary-analyzer

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
# En Linux/macOS:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

#### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### Paso 3: Crear Estructura de Carpetas

```bash
mkdir -p diarios data
```

#### Paso 4: Configurar LM Studio

1. Abrir LM Studio
2. Descargar modelos:
   - **Análisis**: `lmstudio-community/Qwen2.5-7B-Instruct-1M-GGUF`
   - **Chat**: Mismo modelo o `Llama-3.1-8B-Instruct`
3. Iniciar servidor local (pestaña "Server")
4. Verificar que esté en `http://localhost:1234`

---

## 📖 Guía de Uso

### Flujo de Trabajo Completo

#### 1️⃣ Preparar Archivos de Diario

Coloca tus entradas en la carpeta `diarios/` con formato `dd-mm-yyyy.md`:

```
diarios/
├── 01-01-2026.md
├── 15-01-2026.md
└── 31-01-2026.md
```

**Ejemplo de entrada (`15-01-2026.md`):**

```markdown
# 15 de Enero de 2026

Hoy fue un día productivo. Terminé el proyecto que llevaba 
semanas trabajando. Me reuní con María para revisar los 
últimos detalles y todo salió mejor de lo esperado.

Me siento aliviado pero también un poco ansioso por el 
lanzamiento. Espero que todo funcione como planeamos.

## Reflexiones

Aprendí que dividir tareas grandes en pasos pequeños 
realmente funciona. La próxima vez confiaré más en el proceso.
```

#### 2️⃣ Ejecutar Análisis de Diario

```bash
python diary_analyzer.py
```

**Resultado:**
- `data/diario.json` - Análisis completo de cada entrada
- `data/diario_chunks.json` - Chunks semánticos con metadata

**Salida esperada:**

```
============================================================
INICIANDO PROCESAMIENTO BATCH DE DIARIOS
Modo: CON CHUNKING SEMÁNTICO
============================================================
Encontrados 3 archivos de diario en 'diarios'
Archivos pendientes de procesar: 3

[1/3] Procesando...
2026-01-31 10:15:23 - INFO - Analizando: 15-01-2026.md
2026-01-31 10:15:24 - INFO - ✓ Generados 2 chunks para entry_2026_01_15
2026-01-31 10:15:24 - INFO - ✓ 15-01-2026.md procesado exitosamente

============================================================
RESUMEN DEL PROCESAMIENTO
============================================================
Total de archivos: 3
✓ Exitosos: 3
✗ Fallidos: 0
📦 Chunks generados: 7

🎉 ¡Todos los archivos procesados exitosamente!
```

#### 3️⃣ Generar Embeddings

```bash
python embedding_generator.py
```

**Resultado:**
- `data/diario_index.faiss` - Índice vectorial FAISS
- `data/diario_metadata.json` - Metadata de chunks

**Salida esperada:**

```
2026-01-31 10:20:15 | INFO | Cargando modelo de embeddings: intfloat/multilingual-e5-small
2026-01-31 10:20:18 | INFO | Modelo cargado | Dimensión: 384
2026-01-31 10:20:18 | INFO | Cargando chunks desde: data/diario_chunks.json
2026-01-31 10:20:18 | INFO | 7 chunks cargados
2026-01-31 10:20:18 | INFO | Generando embeddings...
Batches: 100%|████████████████████| 1/1 [00:02<00:00,  2.15s/it]
2026-01-31 10:20:20 | INFO | Embeddings generados correctamente
2026-01-31 10:20:20 | INFO | Creando índice FAISS (IndexFlatIP)
2026-01-31 10:20:20 | INFO | Índice FAISS creado | Vectores: 7
2026-01-31 10:20:20 | INFO | ✓ Indexación del diario completada con éxito
```

#### 4️⃣ Iniciar Chatbot Web

```bash
streamlit run app.py
```

**O usar versión terminal:**

```bash
python rag_chat_engine.py
```

El navegador se abrirá automáticamente en `http://localhost:8501`

### Ejemplos de Consultas

**Búsqueda de emociones:**
```
Usuario: "¿Cuándo me sentí más ansioso?"
Sistema: [Busca chunks con ansiedad, muestra fechas y contexto]
```

**Reflexiones sobre temas:**
```
Usuario: "¿Qué he aprendido sobre el trabajo en equipo?"
Sistema: [Recupera reflexiones sobre trabajo, sintetiza aprendizajes]
```

**Patrones temporales:**
```
Usuario: "¿Cómo cambió mi estado de ánimo este mes?"
Sistema: [Analiza emociones a lo largo del tiempo]
```

**Decisiones pasadas:**
```
Usuario: "Dame consejos basados en cómo resolví problemas antes"
Sistema: [Busca situaciones similares, extrae estrategias]
```

---

## 📁 Formato de Archivos

### Entrada: Archivos de Diario

**Ubicación:** `diarios/dd-mm-yyyy.md`

**Formato requerido:**
- Nombre: `dd-mm-yyyy.md` (ej: `15-01-2026.md`)
- Codificación: UTF-8
- Formato: Markdown (opcional)

**Validación:**
- ✅ Fecha válida del calendario
- ✅ Formato exacto del nombre
- ✅ Extensión `.md`

### Salida 1: Análisis Completo (`diario.json`)

```json
[
  {
    "id": "entry_2026_01_15",
    "fecha": "15-01-2026",
    "raw_text": "# 15 de Enero de 2026\n\nHoy fue un día...",
    "summary": "Día productivo finalizando proyecto con María...",
    "emotions": ["aliviado", "ansioso"],
    "topics": ["trabajo", "proyecto", "reunión"],
    "people": ["María"],
    "intensity": "media",
    "word_count": 89,
    "char_count": 542,
    "chunk_count": 2
  }
]
```

**Campos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único (`entry_yyyy_mm_dd`) |
| `fecha` | string | Fecha en formato `dd-mm-yyyy` |
| `raw_text` | string | Texto completo original |
| `summary` | string | Resumen neutral (máx 3 líneas) |
| `emotions` | array | Emociones detectadas |
| `topics` | array | Temas principales |
| `people` | array\|null | Personas mencionadas |
| `intensity` | string | `"baja"` \| `"media"` \| `"alta"` |
| `word_count` | number | Cantidad de palabras |
| `char_count` | number | Cantidad de caracteres |
| `chunk_count` | number | Número de chunks generados |

### Salida 2: Chunks Semánticos (`diario_chunks.json`)

```json
[
  {
    "chunk_id": "entry_2026_01_15_chunk_0",
    "entry_id": "entry_2026_01_15",
    "index": 0,
    "text": "Hoy fue un día productivo. Terminé el proyecto...",
    "word_count": 52,
    "char_count": 289,
    "type": "hechos",
    "metadata": {
      "date": "15-01-2026",
      "emotions": ["aliviado", "ansioso"],
      "topics": ["trabajo", "proyecto"],
      "intensity": "media",
      "people": ["María"]
    }
  }
]
```

**Tipos de chunks:**

- `hechos` - Eventos, acciones, descripciones
- `emociones` - Sentimientos, estados emocionales
- `reflexion` - Pensamientos, aprendizajes
- `mixto` - Combinación de varios tipos

### Salida 3: Índice FAISS (`diario_index.faiss`)

Archivo binario FAISS con vectores de 384 dimensiones (no legible directamente).

### Salida 4: Metadata (`diario_metadata.json`)

Copia de `diario_chunks.json` sin embeddings, usada por el motor de búsqueda.

---

## 🗂️ Estructura del Proyecto

```
diary-analyzer/
├── 📄 README.md                    # Esta documentación
├── 📄 requirements.txt             # Dependencias Python
├── 📄 LICENSE                      # Licencia MIT
├── 📄 CHANGELOG.md                 # Historial de versiones
│
├── 🔧 run.sh                       # Script de instalación y ejecución
│
├── 🐍 diary_analyzer.py            # [1] Análisis y chunking
├── 🐍 embedding_generator.py       # [2] Generación de embeddings
├── 🐍 query_engine.py             # [3] Motor de búsqueda semántica
├── 🐍 rag_chat_engine.py          # [4] Chatbot RAG
├── 🐍 app.py                      # [5] Interfaz web Streamlit
│
├── 📁 diarios/                     # Archivos .md del usuario
│   ├── 01-01-2026.md
│   ├── 15-01-2026.md
│   └── 31-01-2026.md
│
├── 📁 data/                        # Datos generados
│   ├── diario.json                # Análisis completo
│   ├── diario_chunks.json         # Chunks semánticos
│   ├── diario_index.faiss         # Índice vectorial
│   └── diario_metadata.json       # Metadata de chunks
│
└── 📁 .venv/                       # Entorno virtual Python
```

---

## ⚙️ Configuración Avanzada

### Ajustar Parámetros de Chunking

**Archivo:** `diary_analyzer.py`

```python
# Línea ~130
chunks = dividir_en_chunks_semanticos(
    texto,
    min_palabras=100,   # Mínimo de palabras por chunk
    max_palabras=300    # Máximo de palabras por chunk
)
```

**Recomendaciones por caso de uso:**

| Caso | `min_palabras` | `max_palabras` | Razón |
|------|----------------|----------------|-------|
| Diarios cortos | 50 | 150 | Evitar fragmentación |
| Diarios largos | 150 | 400 | Mejor contexto |
| Búsqueda precisa | 80 | 200 | Balance óptimo |
| RAG general | 100 | 300 | Estándar recomendado |

### Cambiar Modelo de Embeddings

**Archivo:** `embedding_generator.py`

```python
# Línea ~55
indexer = DiarioVectorIndexer(
    model_name="intfloat/multilingual-e5-small"  # Cambiar aquí
)
```

**Modelos alternativos:**

| Modelo | Tamaño | Dimensión | Idiomas | Rendimiento |
|--------|--------|-----------|---------|-------------|
| `intfloat/multilingual-e5-small` | 118MB | 384 | 100+ | ⭐⭐⭐⭐ (recomendado) |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 418MB | 384 | 50+ | ⭐⭐⭐⭐⭐ |
| `BAAI/bge-m3` | 2.2GB | 1024 | 100+ | ⭐⭐⭐⭐⭐ (mejor calidad) |
| `hiiamsid/sentence_similarity_spanish_es` | 125MB | 768 | Español | ⭐⭐⭐ |

### Personalizar Prompt del Sistema

**Archivo:** `rag_chat_engine.py`

```python
# Líneas ~10-100
SYSTEM_PROMPT = """
Rol y límites
Eres un asistente de reflexión personal...

[Modificar aquí el comportamiento del chatbot]
"""
```

### Cambiar Temperatura del Modelo

**Archivo:** `rag_chat_engine.py`

```python
# Línea ~140
payload = {
    "model": MODEL_NAME,
    "messages": mensajes,
    "temperature": 0.4  # Valores: 0.0 (determinista) a 1.0 (creativo)
}
```

**Guía de temperatura:**

| Temperatura | Comportamiento | Uso recomendado |
|-------------|----------------|------------------|
| 0.0 - 0.3 | Muy consistente | Análisis técnico |
| 0.4 - 0.6 | Balance | Reflexión personal ✅ |
| 0.7 - 1.0 | Creativo | Escritura exploratoria |

### Ajustar Cantidad de Chunks Recuperados

**Archivo:** `rag_chat_engine.py`

```python
# Línea ~118
resultados = self.engine.buscar(pregunta, k=5)  # Cambiar valor de k
```

**Recomendaciones:**

- `k=3` - Respuestas concisas
- `k=5` - Balance estándar ✅
- `k=10` - Contexto amplio (puede ser redundante)

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### ❌ Error: "No se pudo conectar con LM Studio"

**Causa:** El servidor de LM Studio no está corriendo.

**Solución:**
1. Abrir LM Studio
2. Ir a la pestaña "Server"
3. Click en "Start Server"
4. Verificar que muestra `http://localhost:1234`

#### ❌ Error: "No se encontró un bloque JSON válido"

**Causa:** El modelo LLM devolvió respuesta mal formateada.

**Solución:**
1. Usar un modelo más grande (mínimo 7B)
2. Verificar que el modelo está completamente cargado
3. Reducir `temperature` a 0.3 para respuestas más consistentes

#### ❌ Error: "FAISS index not found"

**Causa:** No se generaron los embeddings.

**Solución:**
```bash
# Ejecutar nuevamente el generador
python embedding_generator.py
```

#### ❌ Los chunks son muy pequeños o muy grandes

**Solución:** Ajustar parámetros en `diary_analyzer.py`:

```python
# Para chunks más grandes:
min_palabras=150
max_palabras=400

# Para chunks más pequeños:
min_palabras=50
max_palabras=150
```

#### ❌ Error de memoria con embeddings

**Causa:** Modelo demasiado grande para tu RAM.

**Solución:**
1. Cambiar a modelo más pequeño:
   ```python
   model_name="intfloat/multilingual-e5-small"  # Solo 118MB
   ```
2. Procesar en batches más pequeños

#### ❌ El chatbot no encuentra contexto relevante

**Causa:** Query muy diferente del lenguaje del diario.

**Solución:**
1. Reformular pregunta con palabras del diario
2. Aumentar `k` (chunks recuperados) a 7-10
3. Verificar que los embeddings se generaron correctamente

### Logs y Debugging

**Ver logs detallados:**

```bash
# Activar modo debug en diary_analyzer.py
logging.basicConfig(level=logging.DEBUG)
```

**Verificar archivos generados:**

```bash
# Comprobar que existen
ls -lh data/

# Ver contenido de chunks
python -m json.tool data/diario_chunks.json | head -50

# Verificar índice FAISS
python -c "import faiss; index = faiss.read_index('data/diario_index.faiss'); print(f'Vectores: {index.ntotal}')"
```

---

## 🗺️ Roadmap

### ✅ Versión 1.0.0 (Actual) - Enero 2026

Sistema base funcional con todas las piezas integradas.

**Características:**
- ✅ Análisis de diario con LLM local
- ✅ Chunking semántico automático
- ✅ Generación de embeddings multilingües
- ✅ Índice vectorial FAISS
- ✅ Motor de búsqueda semántica
- ✅ Chatbot RAG con interfaz web
- ✅ Pipeline automatizado con `run.sh`

---

### 🔄 Versión 1.1.0 - Memoria a Corto Plazo (Febrero 2026)

**Objetivo:** Conversaciones multi-turno con contexto persistente.

**Nuevas características:**
- [ ] Historial de conversación por sesión
- [ ] Memoria de referencias previas en el chat
- [ ] Seguimiento de contexto entre preguntas relacionadas
- [ ] Comando `/reset` para limpiar memoria
- [ ] Guardar sesiones de chat en JSON

**Implementación:**
```python
# rag_chat_engine.py
class DiarioRAGChat:
    def __init__(self):
        self.conversation_history = []  # Nuevo
        self.context_window = 5  # Últimos 5 intercambios
    
    def preguntar(self, pregunta):
        # Incluir historial en prompt
        # Mantener contexto coherente
```

**Beneficios:**
- Conversaciones más naturales
- "¿Y qué pasó después?" sin repetir contexto
- Seguimiento de temas a lo largo de la sesión

---

### 📦 Versión 1.2.0 - Versionado del Diario (Marzo 2026)

**Objetivo:** Control de versiones tipo Git para entradas de diario.

**Nuevas características:**
- [ ] Sistema de commits para cambios
- [ ] Historial de modificaciones por entrada
- [ ] Comparación de versiones (diff)
- [ ] Restauración de versiones anteriores
- [ ] Tags para momentos importantes
- [ ] Exportación de historial completo

**Estructura de datos:**
```json
{
  "entry_id": "entry_2026_01_15",
  "versions": [
    {
      "version": 1,
      "timestamp": "2026-01-15T20:30:00Z",
      "text": "...",
      "commit_message": "Entrada inicial"
    },
    {
      "version": 2,
      "timestamp": "2026-01-16T09:00:00Z",
      "text": "...",
      "commit_message": "Añadí reflexión matutina"
    }
  ]
}
```

**Comandos nuevos:**
- `diary commit -m "mensaje"` - Guardar cambios
- `diary log <fecha>` - Ver historial
- `diary diff v1 v2` - Comparar versiones
- `diary restore v1` - Volver a versión anterior

---

### 🎨 Versión 1.3.0 - Mejora de Aplicación Web (Abril 2026)

**Objetivo:** Interfaz profesional y rica en features.

**Nuevas características:**
- [ ] Editor de markdown integrado
- [ ] Visualización de contexto recuperado
- [ ] Gráficos de emociones temporales
- [ ] Timeline interactivo del diario
- [ ] Búsqueda avanzada con filtros
- [ ] Temas claro/oscuro
- [ ] Exportación directa desde UI
- [ ] Modo multi-columna (editor + chat)

**Tecnología:**
- Streamlit mejorado o migración a Gradio
- Plotly para visualizaciones
- Ace Editor para markdown

**Mockup de features:**

```
┌────────────────────────────────────────────────────────┐
│  📔 Diario Reflexivo                    [Usuario] [⚙️] │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐  ┌────────────────────────────┐ │
│  │  📝 Editor       │  │  💬 Chat                   │ │
│  │                  │  │                            │ │
│  │  # Hoy fue...    │  │  Tú: ¿Cómo me sentí?      │ │
│  │                  │  │  IA: Según tus entradas... │ │
│  │  [Guardar]       │  │                            │ │
│  └──────────────────┘  └────────────────────────────┘ │
│                                                         │
│  📊 Emociones este mes:  [═══════▓▓▓░░] Ansiedad ↗    │
│                          [══▓▓▓▓░░░░░] Alegría →      │
│                                                         │
│  🔍 [Buscar...] [Filtrar por: Emociones ▼] [Exportar] │
└────────────────────────────────────────────────────────┘
```

**Beneficios:**
- Experiencia de usuario moderna y fluida
- Insights visuales de patrones emocionales
- Productividad mejorada con editor integrado

---

### 🐛 Versión 1.4.0 - Corrección de Errores y Optimización (Mayo 2026)

**Objetivo:** Sistema estable, rápido y confiable.

**Correcciones planificadas:**
- [ ] Fix: Manejo de caracteres especiales en nombres de archivo
- [ ] Fix: Timeout en embeddings de textos muy largos
- [ ] Fix: Chunks duplicados en entradas cortas
- [ ] Fix: Errores de encoding en Windows
- [ ] Fix: Pérdida de contexto en conversaciones largas
- [ ] Optimización: Caché de embeddings frecuentes
- [ ] Optimización: Procesamiento paralelo de chunks
- [ ] Optimización: Reducción de uso de memoria

**Mejoras de rendimiento:**

| Operación | v1.0.0 | v1.4.0 (objetivo) | Mejora |
|-----------|--------|-------------------|--------|
| Análisis de entrada | ~5s | ~2s | 60% ⬇️ |
| Generación de embeddings | ~3s | ~1s | 67% ⬇️ |
| Búsqueda semántica | ~500ms | ~100ms | 80% ⬇️ |
| Respuesta del chatbot | ~4s | ~3s | 25% ⬇️ |

**Tests automatizados:**
- [ ] Suite de tests unitarios (pytest)
- [ ] Tests de integración end-to-end
- [ ] CI/CD con GitHub Actions
- [ ] Cobertura mínima 80%

**Beneficios:**
- Mayor confiabilidad en producción
- Experiencia más rápida y fluida
- Menor consumo de recursos

---

### 🧠 Versión 1.5.0 - Detección de Patrones Emocionales (Junio 2026)

**Objetivo:** Análisis inteligente de tendencias y patrones a largo plazo.

**Nuevas características:**
- [ ] Detección automática de patrones emocionales
- [ ] Alertas de cambios significativos en el estado de ánimo
- [ ] Correlación de emociones con eventos/personas
- [ ] Predicción de estados emocionales futuros
- [ ] Recomendaciones personalizadas basadas en patrones
- [ ] Reportes mensuales/trimestrales automáticos

**Algoritmos implementados:**

1. **Análisis de tendencias temporales:**
   ```python
   # Detectar si la ansiedad aumentó/disminuyó
   trend = analyze_emotion_trend("ansiedad", days=30)
   # trend: "increasing" | "decreasing" | "stable"
   ```

2. **Correlación de eventos:**
   ```python
   # ¿Qué personas/actividades se asocian con alegría?
   correlations = find_correlations("alegría")
   # {"María": 0.8, "proyecto": 0.6, "ejercicio": 0.9}
   ```

3. **Detección de anomalías:**
   ```python
   # Alertar si hay cambio drástico
   if emotional_variance > threshold:
       notify("Tu estado emocional cambió significativamente")
   ```

**Panel de análisis:**

```
┌────────────────────────────────────────────────────────┐
│  📈 Análisis de Patrones Emocionales                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  🔍 Patrón detectado:                                  │
│  "Tu ansiedad tiende a aumentar los lunes y           │
│   disminuir cuando mencionas ejercicio"                │
│                                                         │
│  📊 Últimos 30 días:                                   │
│   Alegría:    ████████░░ 78% (↗ +12%)                 │
│   Ansiedad:   ████░░░░░░ 42% (↘ -8%)                  │
│   Motivación: ██████████ 89% (→ estable)              │
│                                                         │
│  💡 Recomendación:                                     │
│  "Considera mantener tu rutina de ejercicio, está     │
│   correlacionada con estados emocionales positivos"    │
│                                                         │
│  [Ver reporte completo] [Exportar análisis]           │
└────────────────────────────────────────────────────────┘
```

**Tecnología:**
- Scikit-learn para análisis estadístico
- Pandas para manipulación de series temporales
- Matplotlib/Plotly para visualizaciones avanzadas

**Beneficios:**
- Autoconocimiento profundo basado en datos
- Detección temprana de cambios emocionales
- Recomendaciones personalizadas accionables

---

### 📄 Versión 2.0.0 - Exportación Avanzada (Julio 2026)

**Objetivo:** Flexibilidad total en formatos de salida.

**Nuevas características:**
- [ ] Exportación a PDF con diseño profesional
- [ ] Exportación a Markdown con metadata
- [ ] Generación de reportes HTML interactivos
- [ ] Exportación a formato Notion/Obsidian
- [ ] Backup completo del sistema (ZIP)
- [ ] Importación desde otros formatos
- [ ] Plantillas personalizables de exportación

**Formatos soportados:**

| Formato | Contenido | Personalizable | Casos de uso |
|---------|-----------|----------------|--------------|
| **PDF** | Diario completo + gráficos | ✅ Sí | Impresión, archivo permanente |
| **Markdown** | Texto + metadata YAML | ✅ Sí | Obsidian, Notion, GitHub |
| **HTML** | Sitio web estático | ✅ Sí | Publicación online |
| **JSON** | Datos estructurados | ❌ Estándar | Backup, migración |
| **CSV** | Análisis tabular | ✅ Sí | Excel, análisis estadístico |
| **EPUB** | Libro electrónico | ✅ Sí | Lectura en e-readers |

**Ejemplo de exportación a PDF:**

```bash
# Exportar enero 2026 con gráficos
python export.py --format pdf \
                 --start 01-01-2026 \
                 --end 31-01-2026 \
                 --include-charts \
                 --template elegant

# Resultado: diario_2026_enero.pdf (120 páginas, diseño profesional)
```

**Plantillas de exportación:**

```python
# templates/pdf_template.py
TEMPLATES = {
    "minimal": {
        "fonts": "Helvetica",
        "colors": "grayscale",
        "charts": False
    },
    "elegant": {
        "fonts": "Crimson Text",
        "colors": "earth_tones",
        "charts": True,
        "cover_page": True
    },
    "technical": {
        "fonts": "Roboto Mono",
        "colors": "blue_accent",
        "charts": True,
        "code_highlighting": True
    }
}
```

**Funciones avanzadas:**
- [ ] Marca de agua personalizada
- [ ] Encriptación de PDF con contraseña
- [ ] Generación de índice automático
- [ ] Inclusión de imágenes adjuntas
- [ ] Anonimización de nombres (para compartir)

**Beneficios:**
- Portabilidad completa de tus datos
- Compatibilidad con otras herramientas
- Opciones para compartir o archivar
- Control total sobre tus reflexiones

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Este proyecto busca mejorar continuamente.

### Formas de Contribuir

- 🐛 **Reportar bugs** - Abre un [issue](https://github.com/fabricioarce/diary-analyzer/issues)
- 💡 **Sugerir features** - Comparte tus ideas
- 📝 **Mejorar documentación** - Clarifica, corrige, expande
- 💻 **Contribuir código** - Implementa nuevas funcionalidades
- 🌍 **Traducciones** - Ayuda a soportar más idiomas

### Proceso de Contribución

1. **Fork** el repositorio
2. **Crea una rama** para tu feature:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. **Haz commit** de tus cambios:
   ```bash
   git commit -m "feat: descripción clara del cambio"
   ```
4. **Push** a tu fork:
   ```bash
   git push origin feature/nombre-descriptivo
   ```
5. **Abre un Pull Request** con descripción detallada

### Convenciones de Código

- **Estilo:** PEP 8 para Python
- **Docstrings:** Google style
- **Tests:** Pytest para nuevas funcionalidades
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/)

### Áreas Prioritarias

- [ ] Tests automatizados
- [ ] Soporte para otros idiomas
- [ ] Optimización de rendimiento
- [ ] Integración con más modelos LLM
- [ ] Mejoras en la UI

---

## 🔒 Privacidad

Este proyecto fue diseñado con **privacidad total** como principio fundamental.

### Garantías de Privacidad

✅ **100% Local** - Todo el procesamiento ocurre en tu computadora  
✅ **Sin telemetría** - No se recopilan datos de uso  
✅ **Sin conexiones externas** - Ningún dato sale de tu máquina  
✅ **Sin servicios cloud** - No hay APIs de terceros  
✅ **Control total** - Tus datos permanecen contigo siempre

### Dónde Están Tus Datos

| Tipo de dato | Ubicación | Acceso |
|--------------|-----------|--------|
| Archivos .md originales | `diarios/` | Solo tú |
| Análisis y chunks | `data/*.json` | Solo tú |
| Índice vectorial | `data/*.faiss` | Solo tú |
| Historial de chat | `data/sessions/` | Solo tú |

### Recomendaciones de Seguridad

1. **Backups regulares:**
   ```bash
   # Backup automático
   tar -czf backup_$(date +%Y%m%d).tar.gz diarios/ data/
   ```

2. **Encriptación opcional:**
   ```bash
   # Encriptar carpeta completa
   gpg --symmetric --cipher-algo AES256 backup.tar.gz
   ```

3. **Control de versiones:**
   ```bash
   # Usa Git para historial (añade .gitignore)
   echo "data/" >> .gitignore
   git init
   ```

### Modelo de Amenazas

❌ **NO protege contra:**
- Acceso físico no autorizado a tu computadora
- Malware o keyloggers en tu sistema
- Pérdida de datos por fallos de hardware

✅ **SÍ protege contra:**
- Filtración de datos a servicios cloud
- Rastreo por terceros
- Compartición no consentida de información personal

---

## 📜 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.

```
Copyright (c) 2026 Fabricio Arce

Por la presente se concede permiso, libre de cargos, a cualquier persona
que obtenga una copia de este software y de los archivos de documentación
asociados (el "Software"), a utilizar el Software sin restricción...
```

**Ver archivo completo:** [LICENSE](LICENSE)

### ¿Qué significa esto?

✅ **Puedes:**
- Usar el software para cualquier propósito
- Modificar el código fuente
- Distribuir copias
- Sublicenciar tu versión modificada
- Usar en proyectos comerciales

❌ **Debes:**
- Incluir el aviso de copyright en las copias
- Incluir la licencia MIT en distribuciones

❌ **No hay garantía:** El software se proporciona "tal cual"

---

## 🙏 Agradecimientos

Este proyecto no sería posible sin:

- **[LM Studio](https://lmstudio.ai)** - Plataforma local de LLMs que hace posible la privacidad total
- **[Sentence Transformers](https://www.sbert.net/)** - Biblioteca excepcional de embeddings semánticos
- **[FAISS](https://github.com/facebookresearch/faiss)** - Motor de búsqueda vectorial ultrarrápido de Meta AI
- **[Streamlit](https://streamlit.io/)** - Framework que simplifica la creación de interfaces web
- **[Anthropic](https://www.anthropic.com)** - Por Claude, quien ayudó en el desarrollo de este proyecto

### Inspiración

Este proyecto se inspira en:
- **Obsidian** - Filosofía de datos locales y vinculación de conocimiento
- **Logseq** - Journaling estructurado y consultas avanzadas
- **Notion AI** - Interacción natural con datos personales
- **Open-source RAG projects** - Comunidad que hace posible la IA local

---

## 📞 Soporte y Contacto

### Documentación

- 📖 **README completo** - Este archivo
- 📋 **CHANGELOG** - [Ver historial de versiones](CHANGELOG.md)
- 🐛 **Issues** - [Reportar problemas](https://github.com/fabricioarce/diary-analyzer/issues)
- 💬 **Discussions** - [Hacer preguntas](https://github.com/fabricioarce/diary-analyzer/discussions)

### Autor

**Fabricio Arce**

- GitHub: [@fabricioarce](https://github.com/fabricioarce)
- Email: [Crear issue para contacto](https://github.com/fabricioarce/diary-analyzer/issues/new)

### Comunidad

¿Usas este proyecto? ¡Comparte tu experiencia!

- ⭐ **Dale una estrella** en GitHub si te resulta útil
- 🐦 **Comparte** en redes sociales
- 📝 **Escribe** sobre tu experiencia
- 🤝 **Contribuye** con código o ideas

---

## 🎯 Estado del Proyecto

```
📊 Versión actual: 1.0.0 (Estable)
🔧 En desarrollo activo: ✅ Sí
📅 Última actualización: Enero 2026
🐛 Issues abiertos: Ver GitHub
⭐ Estrellas: [Tu apoyo cuenta]
```

### Hoja de Ruta Resumida

| Versión | Estado | Fecha estimada | Foco principal |
|---------|--------|----------------|----------------|
| 1.0.0 | ✅ **Completado** | Enero 2026 | Sistema base funcional |
| 1.1.0 | 🔄 Planificado | Febrero 2026 | Memoria de conversación |
| 1.2.0 | 📋 Planificado | Marzo 2026 | Versionado del diario |
| 1.3.0 | 📋 Planificado | Abril 2026 | Mejora de UI/UX |
| 1.4.0 | 📋 Planificado | Mayo 2026 | Optimización y bugs |
| 1.5.0 | 📋 Planificado | Junio 2026 | Análisis de patrones |
| 2.0.0 | 💡 Idea | Julio 2026 | Exportación avanzada |

---

## 💝 Nota Final

Este proyecto nació de la necesidad personal de tener un diario inteligente que respetara completamente la privacidad. Si te identificas con esta visión, espero que encuentres valor en esta herramienta.

La reflexión personal es un viaje íntimo, y tus pensamientos merecen estar en un lugar seguro, accesible y que te ayude a crecer. Este sistema busca ser ese compañero silencioso que te escucha sin juzgar, recuerda sin olvidar, y te acompaña sin invadir.

**Gracias por confiar en este proyecto.** 🙏

---

<div align="center">

### ¿Te resultó útil este proyecto?

⭐ **Dale una estrella en GitHub**  
🐛 **Reporta bugs para mejorarlo**  
💡 **Sugiere nuevas funcionalidades**  
🤝 **Contribuye con código**

**Hecho con ❤️ y respeto por tu privacidad**

[⬆ Volver arriba](#-diario-reflexivo-con-ia)

</div>

---

> **Disclaimer:** Este software se proporciona como herramienta de reflexión personal y no sustituye asistencia profesional en salud mental. Si experimentas dificultades emocionales significativas, consulta con un profesional calificado.