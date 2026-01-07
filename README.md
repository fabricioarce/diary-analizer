# 📔 Diario IA — Tu Memoria Personal Inteligente

> Transforma tus reflexiones diarias en una base de conocimientos privada y chatea con tu "yo" del pasado usando Inteligencia Artificial.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Astro](https://img.shields.io/badge/Astro-5.0-FF5D01?style=flat&logo=astro&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi&logoColor=white)

---

## 🌟 ¿Qué es Diario IA?

¿Alguna vez has querido preguntarle a tu diario cómo te sentías hace un año? ¿O qué patrones de pensamiento se repiten en tu vida? **Diario IA** hace esto posible.

1.  **Analiza**: Lee tus archivos `.md` de diario y extrae emociones y temas.
2.  **Organiza**: Guarda todo en una base de datos "vectorial" (buscable por significado, no solo palabras).
3.  **Conversa**: Te permite chatear con tus propios recuerdos usando una IA que respeta tu privacidad.

---

## 🚀 Inicio Rápido (¡Sin complicaciones!)

Si quieres empezar **YA**, sigue estos pasos:

### 1. Preparación
*   Instala [Python 3.10 o superior](https://www.python.org/downloads/).
*   Instala [Node.js](https://nodejs.org/).
*   Consigue una [API Key de Groq](https://console.groq.com/) (es gratis y muy rápida).

### 2. Configuración
Crea un archivo llamado `.env` en la carpeta `backend/app` y pon tu clave:
```env
GROQ_API_KEY=tu_clave_aqui_gs_...
```

### 3. ¡A correr! 🏃‍♂️
Solo tienes que abrir una terminal en la carpeta del proyecto y escribir:
```bash
bash scripts/run.sh
```
*Este script hará TODO por ti: instalará lo que falta, procesará tus diarios y lanzará la aplicación.*

---

## 📚 Guías Detalladas

Si quieres saber más o algo no funciona, mira nuestras guías:

*   **[🐣 Guía para Principiantes](docs/GUIDE_FOR_BEGINNERS.md)**: El manual de "cero a héroe" paso a paso.
*   **[🛠️ Instalación y Configuración](docs/SETUP.md)**: Si prefieres hacer las cosas a mano.
*   **[📖 Cómo usar el sistema](docs/USAGE.md)**: Cómo escribir tus diarios para que la IA los entienda mejor.
*   **[🏗️ Arquitectura Técnica](docs/ARCHITECTURE.md)**: Para los curiosos que quieren saber cómo funciona por dentro.

---

## 🛠️ Tecnologías Utilizadas

*   **Backend**: FastAPI, FAISS (Búsqueda Vectorial), Sentence Transformers.
*   **Frontend**: Astro, React, TailwindCSS.
*   **IA**: Groq API (Llama 3) para velocidad y LM Studio para uso opcional local.

---

> [!TIP]
> **Privacidad Primero**: Tus diarios se procesan localmente o mediante APIs seguras. Nada de lo que escribes se usa para entrenar modelos públicos.