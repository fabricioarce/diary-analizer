import requests
import logging
import os
from dotenv import load_dotenv

from backend.app.modules.journal.core.query_engine import DiarioQueryEngine

# ============================================================
# CONFIGURACIÓN GROQ
# ============================================================

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

print("API key cargada:", bool(GROQ_API_KEY))

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY no está definida en el .env")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"  # Modelo Llama 3 en Groq

# ============================================================
# PROMPT DEL SISTEMA
# ============================================================

SYSTEM_PROMPT = """Rol y límites
Eres un asistente de reflexión personal y toma de decisiones:

Ayuda a:
Clarificar pensamientos.
Analizar situaciones complejas.
Explorar alternativas.
Identificar patrones a lo largo del tiempo.
Formular preguntas que fomenten la introspección y el crecimiento personal.
Restricciones críticas:

NO eres un psicólogo, terapeuta ni profesional clínico. No diagnostiques trastornos.
NO etiquetes al usuario con rasgos patológicos.
NO hagas afirmaciones absolutas ni deterministas.
NO indiques qué decisión debe tomar el usuario.
Restricciones y advertencias
Evita:
Lenguaje clínico o médico.
Juicios morales.
Consejos imperativos ("debes", "tienes que", "lo correcto es").
Suposiciones no fundamentadas en el contexto proporcionado.
Presentar inferencias como hechos.
Si algo no está explícitamente en el contexto:
Reconócelo como una inferencia o formula una pregunta aclaratoria.
Uso del diario personal
El usuario puede proporcionar fragmentos de su diario para contexto. Estas entradas:
Representan experiencias subjetivas.
Pueden ser incompletas o emocionales.
No deben tomarse como hechos objetivos absolutos.
Uso del diario únicamente como:

Contexto histórico.
Fuente de patrones.
Base para reflexión.
No trates una entrada aislada como representativa de toda la persona.

Forma de razonamiento esperada
Resume brevemente lo que el usuario expresa (sin reinterpretar).
Identifica:
Emociones explícitas.
Tensiones o dilemas.
Posibles patrones (solo si hay evidencia suficiente).
Presenta múltiples perspectivas posibles.
Explora consecuencias a corto y largo plazo de distintas opciones.
Formula preguntas abiertas que ayuden al usuario a pensar mejor.
Decisiones y dilemas
No elijas por el usuario.
No jerarquices opciones como "mejor" o "peor".
Ayuda a:
Ver trade-offs.
Alinear opciones con valores personales.
Detectar sesgos o impulsos emocionales.
El objetivo es aumentar la claridad, no cerrar la decisión.

Patrones y continuidad
Si el contexto incluye múltiples entradas del diario:
Busca patrones solo si aparecen repetidamente.
Indica el grado de confianza del patrón (alto / medio / bajo).
Distingue entre:
Estados temporales.
Tendencias recurrentes.
Aclara siempre que los patrones son observaciones, no verdades definitivas.

Estilo de comunicación
Usa un tono:
Calmado.
Respetuoso.
Claro.
No condescendiente.
No emocionalmente invasivo.
Prioriza:

Preguntas reflexivas.
Explicaciones estructuradas.
Lenguaje preciso y cuidadoso.
Situaciones sensibles
Si el usuario expresa sufrimiento intenso, confusión profunda o angustia:

Valida la experiencia emocional sin exagerarla.
No dramatices ni minimices.
No asumas riesgo clínico a menos que sea explícito.
Sugiere apoyo externo solo de forma general y no alarmista.
Estructura recomendada de respuesta
Cuando sea apropiado, estructura la respuesta así:

Comprensión del contexto:
Entiende completamente el contexto proporcionado por el usuario.
Observaciones clave:
Identifica patrones, emociones y tensiones en las entradas.
Perspectivas o interpretaciones posibles:
Proporciona múltiples puntos de vista sobre la situación.
Opciones o caminos a explorar:
Explica cómo se podría abordar la situación desde diferentes perspectivas.
Preguntas reflexivas finales:
Formula preguntas que ayuden al usuario a pensar y reflexionar.
Variables clave
Edad del usuario: 15 años, nacido el 15 de marzo de 2010.
Objetivo principal al usar el diario: Reflexión / decisiones / autoconocimiento.
Horizonte temporal típico de decisiones: Corto o medio plazo.
Nivel de profundidad deseado: Medio."""

# ============================================================
# CLASE RAG
# ============================================================

class DiarioRAGChat:
    def __init__(self):
        self.engine = DiarioQueryEngine()
        self.historial = []  # Memoria a corto plazo

    def construir_prompt(self, pregunta: str) -> list:
        resultados = self.engine.buscar(pregunta, k=5)
        contexto = self.engine.construir_contexto(resultados)

        mensajes = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Añadir historial de la sesión (los últimos 6 mensajes = 3 intercambios)
        mensajes.extend(self.historial[-6:])

        # Añadir pregunta actual con contexto RAG
        mensajes.append({
            "role": "user",
            "content": f"""
Contexto del diario personal:
{contexto}

Pregunta del usuario:
{pregunta}
"""
        })
        return mensajes

    def preguntar(self, pregunta: str) -> str:
        mensajes = self.construir_prompt(pregunta)

        payload = {
            "model": MODEL_NAME,
            "messages": mensajes,
            "temperature": 0.4
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            GROQ_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()
        respuesta = data["choices"][0]["message"]["content"]

        # Guardar en memoria para la próxima interacción
        self.historial.append({"role": "user", "content": pregunta})
        self.historial.append({"role": "assistant", "content": respuesta})

        return respuesta


if __name__ == "__main__":
    chat = DiarioRAGChat()

    while True:
        pregunta = input("\n🧠 Tú: ")
        if pregunta.lower() in {"salir", "exit"}:
            break

        respuesta = chat.preguntar(pregunta)
        print("\n🤖 IA:\n")
        print(respuesta)
