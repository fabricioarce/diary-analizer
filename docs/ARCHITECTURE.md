# 🏗️ Arquitectura del Sistema

Este documento explica cómo funciona **Diario IA** bajo el capó. 

## 🧩 Componentes Principales

El sistema se divide en tres partes que trabajan juntas:

1.  **Motor de Procesamiento** (Python): Lee tus textos y los "entiende".
2.  **Cerebro Vectorial** (FAISS): Almacena tus recuerdos de forma que se puedan buscar por significado.
3.  **Interfaz de Usuario** (Astro + React): La aplicación que ves y con la que chateas.

---

## 🛠️ Detalle Técnico

### 1. El Backend (`backend/app/`)
Construido con **FastAPI**. Es el puente entre tus datos y la interfaz.
*   **`core/diary_analyzer.py`**: Utiliza APIs de IA (Groq o LM Studio) para analizar sentimientos y temas.
*   **`core/embedding_generator.py`**: Convierte el texto en números (vectores) para que la computadora pueda comparar significados.
*   **`core/rag_chat_engine.py`**: Implementa la técnica **RAG** (Generación Aumentada por Recuperación). Busca tus diarios relevantes y se los da a la IA como "contexto" para que sus respuestas sean precisas.

### 2. El Frontend (`frontend/`)
Construido con **Astro** y **React**.
*   Diseñado para ser rápido y fluido.
*   Se comunica con el backend para enviarle tus preguntas y mostrarte las reflexiones.

---

## 🔄 Flujo de Datos

### ¿Cómo se guardan tus recuerdos?
1.  Pones un archivo `.md` en `data/raw/`.
2.  El analyzer extrae la fecha y analiza el sentimiento.
3.  El embedder crea un índice en `data/diario_index.faiss`.

### ¿Cómo funciona el Chat?
1.  Tú escribes: *"¿Cómo me sentía en mi cumpleaños?"*
2.  El sistema busca en `data/diario_index.faiss` los fragmentos que hablan de cumpleaños.
3.  Le envía esos fragmentos a **Groq (Llama 3)**.
4.  La IA te responde: *"En tu cumpleaños te sentías muy feliz porque..."*

---

## 📂 Estructura de Carpetas

```
/
├── backend/app/        # Servidor API y Lógica IA
├── frontend/src/       # Diseño y Pantallas de la Web
├── scripts/            # Script 'run.sh' para inicio rápido
├── data/
│   ├── raw/            # Pon aquí tus archivos .md
│   ├── processed/      # Resultados del análisis
│   └── diary/          # Base de datos vectorial final
└── docs/               # Guías y Manuales
```
