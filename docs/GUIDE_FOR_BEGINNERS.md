# 🐣 Guía para Principiantes: "De Cero a Héroe" con Diario IA

¡Bienvenido! Si no tienes mucha experiencia con programación o terminales, esta guía es para ti. Vamos a configurar todo para que puedas empezar a usar tu diario inteligente en pocos minutos.

---

## 📋 Requisitos Previos

Antes de empezar, asegúrate de instalar estas dos cosas (son como los cimientos de una casa):

1.  **Python**: Descárgalo [aquí](https://www.python.org/downloads/). (Marca la casilla que dice "Add Python to PATH" al instalar).
2.  **Node.js**: Descárgalo [aquí](https://nodejs.org/). Elige la versión "LTS" (es la más estable).
3.  **Groq API Key**: 
    *   Ve a [Groq Console](https://console.groq.com/).
    *   Regístrate (puedes usar Google).
    *   Haz clic en **"API Keys"** y crea una nueva. **Cópiala y guárdala**, la necesitaremos pronto.

---

## 🛠️ Paso 1: Configuración Inicial

1.  **Descarga el proyecto**: Si tienes el código en una carpeta, ábrela.
2.  **Configura tu clave secreta**:
    *   Entra en la carpeta `backend`, luego en `app`.
    *   Busca un archivo llamado `.env` (si no existe, créalo con el bloc de notas).
    *   Escribe esto dentro:
        ```env
        GROQ_API_KEY=tu_clave_de_groq_aqui
        ```
    *   Guarda el archivo.

---

## 📝 Paso 2: Prepara tus Diarios

El sistema lee archivos de texto simples llamados "Markdown" (tienen la extensión `.md`).

1.  Ve a la carpeta `data/raw` (si no existe, créala).
2.  Crea archivos con el nombre de la fecha, por ejemplo: `07-01-2026.md`.
3.  Escribe lo que quieras dentro. ¡Cuanto más escribas, mejor te conocerá la IA!

---

## 🚀 Paso 3: ¡A Funcionar!

No necesitas aprender comandos difíciles. Hemos creado un "botón mágico" para ti.

1.  Abre una terminal (en Windows busca "PowerShell" o "CMD", en Mac/Linux busca "Terminal").
2.  Ve a la carpeta del proyecto.
3.  Escribe esto y pulsa Enter:
    ```bash
    bash scripts/run.sh
    ```
4.  **¿Qué pasará ahora?**
    *   El sistema instalará automáticamente las librerías necesarias.
    *   Analizará tus diarios nuevos.
    *   Abrirá tu navegador predeterminado en `http://localhost:4321`.

---

## 🗨️ Paso 4: Chatea con tu pasado

Una vez que la aplicación cargue en el navegador:
*   Verás una interfaz de chat.
*   Puedes preguntar cosas como: *"¿Cómo me sentí la semana pasada?"* o *"¿Qué temas me han preocupado últimamente?"*.
*   La IA buscará en tus diarios y te responderá con contexto real.

---

## ❓ Preguntas Frecuentes (Troubleshooting)

*   **¿La terminal da error de "command not found"?**: Asegúrate de haber reiniciado tu ordenador después de instalar Python y Node.js.
*   **¿La IA no responde?**: Comprueba que tu `GROQ_API_KEY` sea correcta y que tengas conexión a internet.
*   **¿Puedo usarlo sin internet?**: El sistema está preparado para usar "LM Studio" si quieres privacidad total offline (esto es un poco más avanzado, mira la [Guía de Instalación](SETUP.md)).

---

¡Disfruta de tu viaje de autorreflexión! 🧠✨
