# 🛠️ Guía de Instalación y Configuración

Esta guía es para usuarios que prefieren configurar el sistema manualmente. Si buscas algo más simple, te recomendamos la **[🐣 Guía para Principiantes](GUIDE_FOR_BEGINNERS.md)**.

## 📋 Requisitos Previos

1.  **Python 3.10+**
2.  **Node.js 18+** y un gestor de paquetes (`pnpm`, `npm` o `yarn`).
3.  **Groq API Key**: Necesaria para el Chat ([consíguela aquí](https://console.groq.com)).
4.  **LM Studio** (Opcional): Para análisis local offline.

---

## 🔧 Configuración del Backend

1.  **Entorno Virtual**:
    ```bash
    python -m venv .venv
    # Activar (Linux/Mac): source .venv/bin/activate
    # Activar (Windows): .venv\Scripts\activate
    ```

2.  **Dependencias**:
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Variables de Entorno**:
    Crea `backend/app/.env` con tu clave:
    ```env
    GROQ_API_KEY=gsk_...
    ```

---

## 🎨 Configuración del Frontend

1.  **Instalar y Correr**:
    ```bash
    cd frontend
    pnpm install  # o npm install
    pnpm dev      # o npm run dev
    ```

---

## ⚙️ Uso de LM Studio (Opcional)

Si prefieres no usar Groq para el análisis inicial:
1.  Abre LM Studio e inicia el Local Server (puerto 1234).
2.  Carga un modelo (ej. Llama 3 8B).
3.  El sistema detectará automáticamente el servidor si está activo durante el proceso de análisis.

---

> [!NOTE]
> Para ejecutar todo de una vez sin configurar terminales separadas, usa `bash scripts/run.sh`.

