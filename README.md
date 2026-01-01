# 📔 Analizador de Diario Personal con Chunking Semántico

Herramienta automatizada para analizar entradas de diario personal usando modelos de lenguaje locales (LM Studio). Procesa carpetas completas de diarios, extrae información estructurada y divide el contenido en chunks semánticos preparados para embeddings y RAG (Retrieval Augmented Generation).

## ✨ Características

- 🤖 **Análisis con IA Local**: Utiliza LM Studio para procesamiento privado
- 📁 **Procesamiento Batch**: Analiza carpetas completas automáticamente
- 🔍 **Detección Inteligente**: Solo procesa archivos nuevos, evita duplicados
- 📊 **Extracción Estructurada**: Genera JSON con emociones, temas y resúmenes
- 📅 **Gestión Automática de Fechas**: Extrae y valida fechas del nombre del archivo
- 🧩 **Chunking Semántico**: Divide entradas en fragmentos coherentes (50-300 palabras)
- 🏷️ **Clasificación de Chunks**: Identifica tipos (hechos, emociones, reflexiones)
- 💾 **Doble Almacenamiento**: Análisis completo + chunks separados para RAG
- 🛡️ **Manejo Robusto de Errores**: Validación completa y mensajes claros
- 📝 **Logging Detallado**: Seguimiento completo del proceso con estadísticas
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

### Uso Básico (Procesamiento Batch con Chunking)

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

3. **Resultado**: El script generará dos archivos:
   - `diario.json` - Análisis completos de cada entrada
   - `diario_chunks.json` - Chunks semánticos listos para embeddings

### Ejemplo de Salida

```
============================================================
INICIANDO PROCESAMIENTO BATCH DE DIARIOS
Modo: CON CHUNKING SEMÁNTICO
============================================================
Encontrados 4 archivos de diario en 'diarios'
Archivos pendientes de procesar: 2
Modo: SOLO NUEVOS
Archivos a procesar: 2
------------------------------------------------------------

[1/2] Procesando...
2025-12-31 10:15:23 - INFO - Analizando: 20-12-2025.md (entry_2025_12_20)
2025-12-31 10:15:24 - DEBUG - Texto dividido en 3 chunks
2025-12-31 10:15:24 - INFO - Creados 3 chunks para entry_2025_12_20
2025-12-31 10:15:24 - INFO - ✓ Generados 3 chunks para entry_2025_12_20
2025-12-31 10:15:25 - INFO - ✓ 20-12-2025.md procesado exitosamente

============================================================
RESUMEN DEL PROCESAMIENTO
============================================================
Total de archivos: 2
✓ Exitosos: 2
✗ Fallidos: 0
📦 Chunks generados: 6

🎉 ¡Todos los archivos procesados exitosamente!
============================================================
✓ Procesamiento completado: 2 archivos analizados
📦 Total de chunks generados: 6
============================================================
```

### Configuración Personalizada

Edita las constantes al final de `diary_analyzer.py`:

```python
if __name__ == "__main__":
    CARPETA_DIARIOS = "mis_diarios"         # Tu carpeta
    ARCHIVO_SALIDA = "diario.json"          # Análisis completo
    ARCHIVO_CHUNKS = "diario_chunks.json"   # Chunks para RAG
    MODELO_LLM = "mistral-7b-instruct"      # Modelo diferente
    FORZAR_REPROCESAR = False               # Reprocesar todo
    GENERAR_CHUNKS = True                   # Activar/desactivar chunking
```

### Desactivar Chunking

Si solo quieres el análisis sin chunks:

```python
GENERAR_CHUNKS = False
```

### Uso como Módulo

```python
from diary_analyzer import procesar_carpeta_diarios

# Procesar con chunking
estadisticas = procesar_carpeta_diarios(
    carpeta="diarios",
    ruta_salida="diario.json",
    ruta_chunks="chunks.json",
    generar_chunks=True
)

print(f"Chunks generados: {estadisticas['chunks_generados']}")
```

## 📄 Formatos de Salida

### 1. Archivo de Análisis (`diario.json`)

Análisis completo de cada entrada con texto original:

```json
[
  {
    "id": "entry_2025_12_15",
    "fecha": "15-12-2025",
    "raw_text": "# 15 de Diciembre\n\nHoy fue un día interesante...",
    "summary": "Reunión productiva sobre proyecto con María...",
    "emotions": ["ansioso", "emocionado"],
    "topics": ["trabajo", "programación", "viajes"],
    "people": ["María", "Juan"],
    "intensity": "media",
    "word_count": 342,
    "char_count": 1876,
    "chunk_count": 3
  }
]
```

#### Campos del Análisis

- **id**: Identificador único (`entry_yyyy_mm_dd`)
- **fecha**: Fecha en formato `dd-mm-yyyy`
- **raw_text**: Texto completo original del diario
- **summary**: Resumen neutral en máximo 3 líneas
- **emotions**: Lista de emociones detectadas
- **topics**: Temas principales discutidos
- **people**: Personas mencionadas (null si no hay)
- **intensity**: Intensidad emocional ("baja", "media", "alta")
- **word_count**: Cantidad de palabras
- **char_count**: Cantidad de caracteres
- **chunk_count**: Número de chunks generados

### 2. Archivo de Chunks (`diario_chunks.json`)

Chunks semánticos enriquecidos, listos para convertir en embeddings:

```json
[
  {
    "chunk_id": "entry_2025_12_15_chunk_0",
    "entry_id": "entry_2025_12_15",
    "index": 0,
    "text": "Hoy fue un día interesante. Me reuní con María para discutir el proyecto...",
    "word_count": 156,
    "char_count": 823,
    "type": "hechos",
    "metadata": {
      "date": "15-12-2025",
      "emotions": ["ansioso", "emocionado"],
      "topics": ["trabajo", "programación"],
      "intensity": "media",
      "people": ["María", "Juan"]
    }
  },
  {
    "chunk_id": "entry_2025_12_15_chunk_1",
    "entry_id": "entry_2025_12_15",
    "index": 1,
    "text": "Me sentí un poco ansioso al principio...",
    "word_count": 98,
    "char_count": 512,
    "type": "emociones",
    "metadata": {
      "date": "15-12-2025",
      "emotions": ["ansioso", "emocionado"],
      "topics": ["trabajo", "programación"],
      "intensity": "media",
      "people": ["María", "Juan"]
    }
  }
]
```

#### Campos de Chunks

- **chunk_id**: ID único del chunk
- **entry_id**: ID de la entrada padre
- **index**: Posición del chunk (0, 1, 2...)
- **text**: Contenido textual del chunk (100-300 palabras)
- **word_count**: Palabras en el chunk
- **char_count**: Caracteres en el chunk
- **type**: Tipo de contenido ("hechos", "emociones", "reflexion", "mixto")
- **metadata**: Información contextual heredada del análisis

### Tipos de Chunks

El sistema clasifica automáticamente cada chunk:

- **hechos**: Eventos, acciones, descripción de actividades
- **emociones**: Sentimientos, estados emocionales explícitos
- **reflexion**: Pensamientos, aprendizajes, introspección
- **mixto**: Combinación de varios tipos

## 🔮 Próximos Pasos: Embeddings y RAG

### ¿Por qué Chunking?

El chunking prepara tus diarios para:

1. **Búsqueda Semántica**: Encontrar entradas por significado, no solo palabras
2. **Chatbot de Diario**: Conversar con tus memorias usando IA
3. **Análisis de Patrones**: Detectar tendencias emocionales a lo largo del tiempo
4. **Recomendaciones**: "Días similares a hoy", "Cuando te sentías así..."

### Roadmap de Embeddings (Futuro)

#### Fase 1: Generar Embeddings

```python
# FUTURO - No implementado aún
from sentence_transformers import SentenceTransformer
import json

# 1. Cargar modelo de embeddings (pequeño y rápido)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# o para mejor calidad (más pesado):
# model = SentenceTransformer('BAAI/bge-small-en-v1.5')

# 2. Cargar chunks
with open('diario_chunks.json', 'r') as f:
    chunks = json.load(f)

# 3. Generar embeddings
for chunk in chunks:
    embedding = model.encode(chunk['text'])
    chunk['embedding'] = embedding.tolist()

# 4. Guardar chunks con embeddings
with open('diario_chunks_embedded.json', 'w') as f:
    json.dump(chunks, f)
```

**Modelos recomendados para español**:
- `hiiamsid/sentence_similarity_spanish_es` (ligero)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingüe)

#### Fase 2: Crear Base de Datos Vectorial

```python
# FUTURO - No implementado aún
import faiss
import numpy as np

# Opción A: FAISS (más simple, local)
embeddings = np.array([chunk['embedding'] for chunk in chunks])
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, 'diario_vectors.index')

# Opción B: ChromaDB (más features)
import chromadb

client = chromadb.Client()
collection = client.create_collection("diario")

for chunk in chunks:
    collection.add(
        embeddings=[chunk['embedding']],
        documents=[chunk['text']],
        metadatas=[chunk['metadata']],
        ids=[chunk['chunk_id']]
    )
```

#### Fase 3: Búsqueda Semántica

```python
# FUTURO - Ejemplo de búsqueda
def buscar_en_diario(query, top_k=5):
    # Convertir query a embedding
    query_embedding = model.encode(query)
    
    # Buscar similares
    distances, indices = index.search(
        np.array([query_embedding]), 
        top_k
    )
    
    # Devolver chunks relevantes
    resultados = [chunks[i] for i in indices[0]]
    return resultados

# Uso
resultados = buscar_en_diario("días donde me sentí ansioso")
for chunk in resultados:
    print(f"Fecha: {chunk['metadata']['date']}")
    print(f"Texto: {chunk['text'][:100]}...")
```

#### Fase 4: RAG con Modelo Local (8B)

```python
# FUTURO - Chatbot con memoria
import lmstudio as lms

def chatear_con_diario(pregunta):
    # 1. Buscar contexto relevante
    chunks_relevantes = buscar_en_diario(pregunta, top_k=3)
    contexto = "\n\n".join([c['text'] for c in chunks_relevantes])
    
    # 2. Construir prompt con contexto
    prompt = f"""
    Basándote SOLO en estos fragmentos de mi diario:
    
    {contexto}
    
    Responde a mi pregunta: {pregunta}
    
    Sé empático y personal. Usa "tú" para dirigirte a mí.
    """
    
    # 3. Usar modelo local (ej: Llama-3-8B, Mistral-7B)
    with lms.Client() as client:
        model = client.llm.model("llama-3-8b-instruct")
        response = model.respond(prompt)
        return response.content

# Uso
respuesta = chatear_con_diario("¿Cómo me sentí en diciembre?")
print(respuesta)
```

### Modelos Recomendados para RAG (8B locales)

1. **Llama 3.1 8B Instruct** - Excelente balance calidad/velocidad
2. **Mistral 7B Instruct** - Muy rápido, buena calidad
3. **Phi-3 Medium (14B)** - Si tienes más RAM
4. **Gemma 2 9B** - Alternativa de Google

### Herramientas para el Pipeline Completo

```bash
# Instalar dependencias futuras
pip install sentence-transformers
pip install faiss-cpu  # o faiss-gpu si tienes NVIDIA
pip install chromadb   # alternativa a FAISS
pip install numpy
```

### Arquitectura Futura del Sistema

```
┌─────────────────┐
│  diarios/*.md   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ diary_analyzer  │ ← ACTUAL
│  .py (LLM 2.6B) │
└────────┬────────┘
         │
         ├─► diario.json (análisis)
         │
         └─► diario_chunks.json (chunks)
                    │
                    ▼
         ┌──────────────────┐
         │  embedding.py    │ ← FUTURO
         │  (all-MiniLM)    │
         └─────────┬────────┘
                   │
                   └─► diario_vectors.db
                              │
                              ▼
                   ┌──────────────────┐
                   │   rag_chat.py    │ ← FUTURO
                   │  (Llama 3 8B)    │
                   └──────────────────┘
```

### Casos de Uso Futuros

1. **Búsqueda Contextual**:
   ```
   Usuario: "días donde estuve con María"
   Sistema: [muestra chunks relevantes con fechas]
   ```

2. **Análisis Temporal**:
   ```
   Usuario: "¿cómo cambió mi ansiedad este mes?"
   Sistema: [busca chunks de "ansiedad", analiza tendencia]
   ```

3. **Conversación Natural**:
   ```
   Usuario: "dame consejos basados en cómo superé problemas antes"
   Sistema: [busca entradas de superación, genera consejo]
   ```

4. **Reflexión Asistida**:
   ```
   Usuario: "¿qué he aprendido sobre el trabajo?"
   Sistema: [busca reflexiones sobre trabajo, sintetiza]
   ```

## 🔧 Configuración Avanzada

### Ajustar Tamaño de Chunks

En `diary_analyzer.py`, modifica la función `dividir_en_chunks_semanticos`:

```python
chunks = dividir_en_chunks_semanticos(
    texto,
    min_palabras=50,   # Mínimo por chunk
    max_palabras=200   # Máximo por chunk
)
```

**Recomendaciones**:
- **Para embeddings pequeños** (all-MiniLM): 100-300 palabras
- **Para embeddings grandes** (bge-large): 200-500 palabras
- **Para textos cortos**: reduce a 50-150 palabras

### Personalizar Clasificación de Chunks

Edita las palabras clave en `clasificar_tipo_chunk()`:

```python
# Agregar tus propias palabras indicadoras
palabras_emocionales = [
    'sentí', 'siento', 'feliz', 'triste',
    # Agrega más según tu vocabulario
]
```

## 🐛 Solución de Problemas

### No se generan chunks

**Causa**: `GENERAR_CHUNKS = False` o texto muy corto

**Solución**: 
- Verifica que `GENERAR_CHUNKS = True`
- Asegúrate de que las entradas tengan al menos 100 palabras

### Chunks muy grandes o pequeños

**Solución**: Ajusta los parámetros de `dividir_en_chunks_semanticos()`

### Tipo de chunk siempre "mixto"

**Causa**: Las palabras clave no coinciden con tu vocabulario

**Solución**: Personaliza las listas de palabras en `clasificar_tipo_chunk()`

### Archivo chunks.json muy grande

**Normal**: Si tienes muchas entradas, considera:
- Usar base de datos vectorial en lugar de JSON
- Comprimir el archivo: `gzip diario_chunks.json`

## 📁 Estructura del Proyecto

```
diary-analyzer/
├── diary_analyzer.py           # Script principal
├── README.md                   # Esta documentación
├── requirements.txt            # Dependencias
├── .venv/                      # Entorno virtual
├── diarios/                    # Carpeta con archivos .md
│   ├── 01-12-2025.md
│   ├── 15-12-2025.md
│   └── 31-12-2025.md
├── diario.json                # Análisis completos (generado)
└── diario_chunks.json         # Chunks semánticos (generado)

# Futuros archivos (no implementados aún)
├── embedding_generator.py     # FUTURO: Generar embeddings
├── vector_db.py              # FUTURO: Gestión de vectores
├── rag_chat.py               # FUTURO: Chatbot con RAG
└── diario_vectors.db         # FUTURO: Base de datos vectorial
```

## 🔒 Privacidad y Seguridad

- ✅ Todo el procesamiento es **100% local**
- ✅ No se envían datos a servicios externos
- ✅ Tus diarios permanecen en tu computadora
- ✅ Los embeddings (futuros) también serán locales
- ✅ Sin conexión a internet requerida (excepto instalación inicial)

## 🤝 Contribuciones

Las contribuciones son bienvenidas, especialmente:

- [ ] Implementación de generación de embeddings
- [ ] Integración con ChromaDB/FAISS
- [ ] Sistema RAG completo
- [ ] Interfaz de chat
- [ ] Mejoras en clasificación de chunks

Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/embeddings`)
3. Commit tus cambios (`git commit -m 'feat: agregar embeddings'`)
4. Push a la rama (`git push origin feature/embeddings`)
5. Abre un Pull Request

## 📝 Ejemplos de Uso

### Analizar Estadísticas de Chunks

```python
import json
from collections import Counter

# Cargar chunks
with open('diario_chunks.json') as f:
    chunks = json.load(f)

# Tipos de chunks más comunes
tipos = [c['type'] for c in chunks]
print(Counter(tipos))

# Chunks por entrada
from collections import defaultdict
chunks_por_entrada = defaultdict(int)
for c in chunks:
    chunks_por_entrada[c['entry_id']] += 1

print(f"Promedio de chunks por entrada: {sum(chunks_por_entrada.values()) / len(chunks_por_entrada):.2f}")
```

### Buscar Chunks por Tipo

```python
def buscar_por_tipo(tipo, limite=5):
    with open('diario_chunks.json') as f:
        chunks = json.load(f)
    
    resultado = [c for c in chunks if c['type'] == tipo]
    return resultado[:limite]

# Ver chunks de emociones
emociones = buscar_por_tipo('emociones')
for chunk in emociones:
    print(f"Fecha: {chunk['metadata']['date']}")
    print(f"Texto: {chunk['text'][:100]}...")
    print()
```

### Exportar Chunks a CSV

```python
import csv

def exportar_chunks_csv(archivo_salida='chunks.csv'):
    with open('diario_chunks.json') as f:
        chunks = json.load(f)
    
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        campos = ['chunk_id', 'entry_id', 'date', 'type', 'text', 'word_count']
        writer = csv.DictWriter(f, fieldnames=campos)
        
        writer.writeheader()
        for chunk in chunks:
            writer.writerow({
                'chunk_id': chunk['chunk_id'],
                'entry_id': chunk['entry_id'],
                'date': chunk['metadata']['date'],
                'type': chunk['type'],
                'text': chunk['text'],
                'word_count': chunk['word_count']
            })

exportar_chunks_csv()
```

## 🗺️ Roadmap

### Versión Actual (2.0)
- [x] Procesamiento batch de carpetas
- [x] Chunking semántico automático
- [x] Clasificación de tipos de chunks
- [x] Doble almacenamiento (análisis + chunks)

### Próximas Versiones

**v2.1 - Embeddings** (próximo)
- [ ] Script para generar embeddings
- [ ] Integración con sentence-transformers
- [ ] Soporte para modelos en español
- [ ] Actualización incremental de embeddings

**v2.2 - Base de Datos Vectorial**
- [ ] Integración con FAISS
- [ ] Alternativa con ChromaDB
- [ ] Búsqueda por similitud semántica
- [ ] API de consulta

**v3.0 - RAG Completo**
- [ ] Chatbot conversacional
- [ ] Integración con modelos 8B locales
- [ ] Memoria conversacional
- [ ] Interfaz de chat (CLI)

**v3.1 - Interfaz Gráfica**
- [ ] GUI con Streamlit/Gradio
- [ ] Visualización de embeddings (t-SNE/UMAP)
- [ ] Gráficos de emociones temporales
- [ ] Dashboard interactivo

**Futuro**
- [ ] Análisis de patrones y tendencias
- [ ] Recomendaciones basadas en contexto
- [ ] Exportación a múltiples formatos
- [ ] App móvil (opcional)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

**Fabri**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- [LM Studio](https://lmstudio.ai) por la plataforma local de LLMs
- [Liquid AI](https://liquid.ai) por el modelo LFM
- [Sentence Transformers](https://www.sbert.net/) por los embeddings
- La comunidad de RAG y búsqueda semántica

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Busca en [Issues](https://github.com/tu-usuario/diary-analyzer/issues)
3. Abre un nuevo issue con:
   - Versión de Python
   - Sistema operativo
   - Mensaje de error completo
   - Logs relevantes
   - Ejemplo del archivo de diario (si es posible)

## 🔄 Changelog

### v2.0.0 (2025-01-01) - ACTUAL
- ✨ **Chunking semántico automático**
- ✨ División inteligente por párrafos (100-300 palabras)
- ✨ Clasificación automática de chunks (hechos/emociones/reflexión)
- ✨ Doble almacenamiento: análisis + chunks
- ✨ IDs únicos para entries y chunks
- ✨ Metadata enriquecida en cada chunk
- ✨ Campo `raw_text` en análisis principal
- 📝 Documentación completa sobre embeddings futuros
- 📝 Roadmap detallado para RAG

### v1.1.0 (2024-12-25)
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