# 🏗️ Arquitectura del Sistema: Nexus OS

Este documento explica cómo funciona **Nexus** bajo el capó. 

## 🧩 Componentes Principales

El sistema se basa en una arquitectura de **Monolito Modular**:

1.  **Nexus Dashboard** (Astro + React): La "Shell" central que orquesta la navegación y muestra el estado global de todos los módulos.
2.  **Módulos del Sistema** (FastAPI): Cada funcionalidad (Diario, Creatividad, etc.) vive en su propio espacio aislado dentro de `backend/app/modules/`.
3.  **Core compartido**: Motores de IA, generación de embeddings y bases de datos vectoriales accesibles por todos los módulos.

---

## 🛠️ Detalle Técnico del Módulo Diario IA

### 1. El Backend (`backend/app/modules/journal/`)
*   **`core/diary_analyzer.py`**: Analizador de sentimientos y temas usando LLMs.
*   **`core/embedding_generator.py`**: Motor de vectorización de reflexiones.
*   **`services/diary_service.py`**: Lógica de persistencia y procesamiento en segundo plano.

### 2. El Frontend (`frontend/src/pages/journal/`)
*   Interfaz dedicada para la escritura y exploración de recuerdos.
*   Se conecta a la API modular en `/api/journal/...`.

---

## 📂 Estructura de Carpetas

```
/
├── backend/app/
│   ├── modules/
│   │   └── journal/      # Módulo de Diario (Lógica, API, Core)
│   ├── core/             # Lógica compartida (Excepciones, Base)
│   └── main.py           # Orquestador central de la API
├── frontend/src/
│   ├── pages/
│   │   ├── index.astro   # Dashboard Central
│   │   └── journal/      # Interfaz del Diario
│   └── components/       # Componentes React/Astro
├── data/                 # Bases de datos y archivos brutos
└── docs/                 # Documentación técnica
```
