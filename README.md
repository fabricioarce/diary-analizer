# 🚀 Nexus Personal OS — Tu Memoria Personal Inteligente

> Transforma tus reflexiones en una base de conocimientos privada y gestiona tu vida con un sistema modular impulsado por IA.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Astro](https://img.shields.io/badge/Astro-5.0-FF5D01?style=flat&logo=astro&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi&logoColor=white)

---

## 🌟 ¿Qué es Nexus?

**Nexus** es más que un simple diario; es un sistema operativo personal diseñado para centralizar tu organización, creatividad y toma de decisiones.

1.  **Dashboard Central**: Una vista unificada de todos tus subsistemas activos.
2.  **Módulo Diario IA**: Analiza tus archivos `.md`, extrae emociones y temas, y te permite chatear con tus recuerdos.
3.  **Arquitectura Modular**: Diseñado para crecer. Próximamente incluirá módulos de *Creatividad Pixar* y *Sistemas de Decisión*.

---

## 🚀 Inicio Rápido (¡Sin complicaciones!)

Si quieres empezar **YA**, sigue estos pasos:

### 1. Preparación
*   Instala [Python 3.10 o superior](https://www.python.org/downloads/).
*   Instala [Node.js](https://nodejs.org/).
*   Consigue una [API Key de Groq](https://console.groq.com/).

### 2. Configuración
Crea un archivo llamado `.env` en la carpeta `backend/app` (o en la raíz) y pon tu clave:
```env
GROQ_API_KEY=tu_clave_aqui_gs_...
```

### 3. ¡A correr! 🏃‍♂️
Solo tienes que abrir una terminal en la carpeta del proyecto y escribir:
```bash
bash scripts/run.sh
```
*Este script hará TODO por ti: instalará lo que falta, procesará tus datos y lanzará el Dashboard.*

---

## 📚 Guías Detalladas

*   **[🏗️ Arquitectura Técnica](docs/ARCHITECTURE.md)**: Cómo funciona el sistema por dentro.
*   **[🚀 Visión de Nexus](docs/Architecture_Vision.md)**: El plan para convertir este sistema en tu asistente de vida definitivo.

---

## 🛠️ Tecnologías Utilizadas

*   **Backend**: FastAPI (Arquitectura Modular), FAISS, Sentence Transformers.
*   **Frontend**: Astro 5.0, React, TailwindCSS.
*   **IA**: Groq API (Llama 3) para velocidad y LM Studio para uso opcional local.

---

> [!TIP]
> **Privacidad Primero**: Tus datos se procesan localmente o mediante APIs seguras. Nada de lo que escribes se usa para entrenar modelos públicos.