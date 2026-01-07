# ✅ TODO – Pendientes Técnicos

## 🔴 Alta Prioridad (Infraestructura y Core)
- [ ] **Migración a Base de Datos**: Mover los metadatos de las entradas (fechas, tags, emociones) de archivos JSON planos a SQLite para mejor rendimiento.
- [ ] **Cifrado en Reposo**: Implementar cifrado para los archivos `.md` y la base de datos vectorial.
- [ ] **Refactoreo de Servicios de IA**: Crear una clase base `LLMProvider` para intercambiar fácilmente entre Groq, LM Studio y OpenAI.
- [ ] **Paginación en Frontend**: Manejar correctamente cientos de entradas en la lista de diarios sin degradar el rendimiento.
- [ ] **Validación de Schema**: Usar Pydantic de forma más rigurosa para todas las respuestas de la API.

## 🟡 Media Prioridad (Funcionalidades y UI)
- [ ] **Editor Enriquecido**: Cambiar el textarea simple por un editor Markdown con preview en tiempo real (ej: Milkdown o Tiptap).
- [ ] **Optimización de Embeddings**: Implementar cache de embeddings para no reprocesar archivos que no han cambiado.
- [ ] **Sistema de Logs**: Implementar logging rotativo y niveles de depuración configurables via `.env`.
- [ ] **Tests Automatizados**: Añadir suite de tests con `pytest` para el backend y `Vitest` para el frontend.
- [ ] **Custom Prompts**: Permitir al usuario configurar el "System Prompt" de la IA para cambiar su personalidad.

## 🟢 Baja Prioridad (Mantenimiento y Extra)
- [ ] **Dockerización**: Crear un `Dockerfile` y `docker-compose.yml` para un despliegue en un solo comando.
- [ ] **CI/CD**: Configurar GitHub Actions para linting y testing automático.
- [ ] **Internacionalización (i18n)**: Soporte completo para Inglés/Español en la interfaz.
- [ ] **Documentación de API**: Limpiar y completar los docs de Swagger (`/docs`).

## Done ✅
- [x] Middleware CORS para frontend
- [x] Manejo de errores HTTP
- [x] Validación de entradas básicas
- [x] Actualización automática de embeddings
- [x] Centralización de configuración
- [x] Mockup y layout base
- [x] Editor funcional básico
- [x] Conexión de Chat
- [x] Visualización de emociones
