# 🚀 Guía de Uso y Flujo de Trabajo

Aprende a sacar el máximo provecho a tu **Diario IA**.

## 📝 1. Cómo añadir nuevas entradas

1.  Escribe tus reflexiones en archivos Markdown (`.md`).
2.  Guárdalos en la carpeta `data/raw/` (aquí es donde el sistema busca archivos nuevos).
3.  **Nombre del archivo**: Usa el formato `DD-MM-YYYY.md` (ej. `07-01-2026.md`). 
    *Si usas otro formato, el sistema intentará reconocerlo, pero este es el más seguro.*

---

## 🧠 2. Procesar tus diarios (Análisis)

Para que la IA "lea" tus nuevos diarios, necesitas ejecutar el proceso de análisis. Tienes dos formas:

### Opción A: Botón Todo en Uno (Recomendado)
Ejecuta el script principal:
```bash
bash scripts/run.sh
```
Elige la **Opción 1** para procesar y abrir la web, o la **Opción 3** solo para actualizar los datos.

### Opción B: Manual (Paso a paso)
Si eres usuario avanzado y tienes activado tu entorno virtual:
1.  **Analizar texto**: `python3 -m backend.app.core.diary_analyzer`
2.  **Generar búsqueda**: `python3 -m backend.app.core.embedding_generator`
3.  **Actualizar índice**: `python3 -m backend.app.core.query_engine --build-index`

---

## 💻 3. Usar la Aplicación

Una vez procesados los datos, abre la interfaz:
1.  Ejecuta `bash scripts/run.sh` y elige la **Opción 4** (Solo lanzar frontend).
2.  Entra en `http://localhost:4321`.
3.  ¡Empieza a chatear! Puedes preguntar sobre cualquier cosa que hayas escrito.

---

## ⚡ Consejos para mejores resultados
*   **Sé específico**: En lugar de "Hoy me siento mal", describe *por qué* y *qué pasó*. La IA detectará mejor los patrones.
*   **Usa nombres**: Si mencionas a personas, la IA podrá decirte cuándo aparecieron por última vez.
*   **Formato Markdown**: Puedes usar `# Títulos` o `- Listas` para organizar tus pensamientos; el sistema los entiende perfectamente.
