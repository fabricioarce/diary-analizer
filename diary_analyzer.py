"""
Analizador de Diario Personal con Chunking Semántico
------------------------------------------------------
Script para analizar entradas de diario usando LM Studio y extraer información estructurada.
Incluye sistema de chunking semántico para preparar datos para embeddings futuros.

Uso:
    python diary_analyzer.py

Requisitos:
    - lmstudio
    - Python 3.7+
"""

import re
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any, List, Set, Tuple
from datetime import datetime
import os
import requests
import time
import random
import time

def post_with_retry(
    url: str,
    payload: dict,
    headers: dict,
    max_retries: int = 5,
    base_delay: float = 2.0
):
    """
    POST con retry y backoff exponencial para manejar 429.
    """
    for intento in range(1, max_retries + 1):
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=90
        )

        if response.status_code != 429:
            response.raise_for_status()
            return response

        # 429 → esperar y reintentar
        wait = base_delay * (2 ** (intento - 1))
        jitter = random.uniform(0, 0.5)
        sleep_time = wait + jitter

        logger.warning(
            f"429 Too Many Requests. "
            f"Reintento {intento}/{max_retries} "
            f"esperando {sleep_time:.2f}s"
        )

        time.sleep(sleep_time)

    raise ModelError("Se excedieron los reintentos por rate limit (429)")

# Configuraci'on con api
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY no definida")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiaryAnalyzerError(Exception):
    """Excepción base para errores del analizador de diario"""
    pass


class FileReadError(DiaryAnalyzerError):
    """Error al leer archivos"""
    pass


class JSONParseError(DiaryAnalyzerError):
    """Error al parsear JSON"""
    pass


class ModelError(DiaryAnalyzerError):
    """Error relacionado con el modelo LLM"""
    pass


def generar_id_entrada(fecha: str) -> str:
    """
    Genera un ID único para una entrada de diario.
    
    Args:
        fecha: Fecha en formato dd-mm-yyyy
        
    Returns:
        ID en formato entry_yyyy_mm_dd
    """
    partes = fecha.split('-')
    dia, mes, anio = partes[0], partes[1], partes[2]
    return f"entry_{anio}_{mes}_{dia}"


def generar_id_chunk(entry_id: str, chunk_index: int) -> str:
    """
    Genera un ID único para un chunk.
    
    Args:
        entry_id: ID de la entrada padre
        chunk_index: Índice del chunk
        
    Returns:
        ID en formato entry_yyyy_mm_dd_chunk_N
    """
    return f"{entry_id}_chunk_{chunk_index}"


def validar_nombre_archivo(nombre: str) -> bool:
    """
    Valida que el nombre del archivo siga el formato dd-mm-yyyy.md
    
    Args:
        nombre: Nombre del archivo a validar
        
    Returns:
        True si el formato es válido, False en caso contrario
    """
    patron = r'^\d{2}-\d{2}-\d{4}\.md$'
    return bool(re.match(patron, nombre))


def extraer_fecha_de_nombre(nombre: str) -> Optional[str]:
    """
    Extrae la fecha del nombre del archivo.
    
    Args:
        nombre: Nombre del archivo (ej: "15-12-2025.md")
        
    Returns:
        Fecha en formato dd-mm-yyyy o None si no es válida
    """
    if not validar_nombre_archivo(nombre):
        return None
    
    fecha = nombre.replace('.md', '')
    
    try:
        datetime.strptime(fecha, '%d-%m-%Y')
        return fecha
    except ValueError:
        logger.warning(f"'{nombre}' tiene formato correcto pero fecha inválida")
        return None


def dividir_en_chunks_semanticos(
    texto: str,
    min_palabras: int = 100,
    max_palabras: int = 300
) -> List[str]:
    """
    Divide el texto en chunks semánticos basados en párrafos y longitud.
    
    Args:
        texto: Texto completo a dividir
        min_palabras: Mínimo de palabras por chunk
        max_palabras: Máximo de palabras por chunk
        
    Returns:
        Lista de strings, cada uno un chunk semántico
    """
    # Separar por párrafos (doble salto de línea o headers markdown)
    parrafos = re.split(r'\n\s*\n|(?=^#{1,6}\s)', texto, flags=re.MULTILINE)
    parrafos = [p.strip() for p in parrafos if p.strip()]
    
    chunks = []
    chunk_actual = []
    palabras_actual = 0
    
    for parrafo in parrafos:
        palabras_parrafo = len(parrafo.split())
        
        # Si el chunk actual + este párrafo excede el máximo
        if palabras_actual + palabras_parrafo > max_palabras and chunk_actual:
            # Guardar el chunk actual si tiene suficientes palabras
            if palabras_actual >= min_palabras:
                chunks.append('\n\n'.join(chunk_actual))
                chunk_actual = [parrafo]
                palabras_actual = palabras_parrafo
            else:
                # Si es muy pequeño, agregar este párrafo de todas formas
                chunk_actual.append(parrafo)
                palabras_actual += palabras_parrafo
        else:
            chunk_actual.append(parrafo)
            palabras_actual += palabras_parrafo
    
    # Agregar el último chunk
    if chunk_actual:
        chunks.append('\n\n'.join(chunk_actual))
    
    # Si el texto es muy corto, devolver como un solo chunk
    if not chunks:
        chunks = [texto]
    
    logger.debug(f"Texto dividido en {len(chunks)} chunks")
    return chunks


def clasificar_tipo_chunk(texto: str, analisis: Dict[str, Any]) -> str:
    """
    Clasifica el tipo de contenido del chunk usando heurísticas simples.
    
    Args:
        texto: Contenido del chunk
        analisis: Análisis completo de la entrada
        
    Returns:
        Tipo de chunk: "hechos", "emociones", "reflexion", "mixto"
    """
    texto_lower = texto.lower()
    
    # Palabras indicadoras de emociones
    palabras_emocionales = [
        'sentí', 'siento', 'emoción', 'feliz', 'triste', 'ansioso', 'enojado',
        'frustrado', 'emocionado', 'nervioso', 'alegre', 'deprimido'
    ]
    
    # Palabras indicadoras de reflexión
    palabras_reflexion = [
        'creo', 'pienso', 'reflexión', 'aprendí', 'me di cuenta', 'comprendo',
        'entiendo', 'debería', 'necesito', 'quiero', 'debo'
    ]
    
    # Palabras indicadoras de hechos
    palabras_hechos = [
        'hoy', 'fui', 'hice', 'pasó', 'ocurrió', 'reunión', 'trabajo',
        'proyecto', 'tarea', 'clase', 'estudié'
    ]
    
    puntos_emociones = sum(1 for palabra in palabras_emocionales if palabra in texto_lower)
    puntos_reflexion = sum(1 for palabra in palabras_reflexion if palabra in texto_lower)
    puntos_hechos = sum(1 for palabra in palabras_hechos if palabra in texto_lower)
    
    # Determinar tipo predominante
    puntos = {
        'emociones': puntos_emociones,
        'reflexion': puntos_reflexion,
        'hechos': puntos_hechos
    }
    
    max_puntos = max(puntos.values())
    if max_puntos == 0:
        return 'mixto'
    
    # Si dos categorías están empatadas o muy cerca, es mixto
    top_categorias = [k for k, v in puntos.items() if v == max_puntos]
    if len(top_categorias) > 1:
        return 'mixto'
    
    return top_categorias[0]


def crear_chunks_enriquecidos(
    texto: str,
    analisis: Dict[str, Any],
    entry_id: str,
    modelo: str = "liquidai/lfm2-2.6b-exp@f16"
) -> List[Dict[str, Any]]:
    """
    Crea chunks semánticos enriquecidos usando IA con fallback heurístico.
    """
    try:
        chunks_llm = chunkear_con_llm(texto, modelo)
        logger.info(f"Chunking LLM exitoso ({len(chunks_llm)} chunks)")
    except Exception as e:
        logger.error("Chunking con LLM falló y fallback está desactivado")
        raise
        # logger.warning("Usando fallback heurístico de chunking")
        # chunks_llm = [
        #     {
        #         "index": i,
        #         "type": clasificar_tipo_chunk(t, analisis),
        #         "text": t
        #     }
        #     for i, t in enumerate(dividir_en_chunks_semanticos(texto))
        # ]

    chunks_enriquecidos = []

    for chunk in chunks_llm:
        chunk = sanitizar_chunk(chunk, chunk["text"])
        
        # Validación estricta del tipo
        if chunk.get("type") not in {"hechos", "emociones", "reflexion", "mixto"}:
            logger.warning(
                f"Tipo inválido detectado en chunk {chunk.get('index')}, "
                f"forzando a 'mixto'"
            )
            chunk["type"] = "mixto"

        chunk_texto = chunk["text"]

        chunk_metadata = chunk.get("metadata") or {}

        enriched = {
            "chunk_id": generar_id_chunk(entry_id, chunk["index"]),
            "entry_id": entry_id,
            "index": chunk["index"],
            "text": chunk_texto,
            "word_count": len(chunk_texto.split()),
            "char_count": len(chunk_texto),
            "type": chunk.get("type"),
            "metadata": {
                **chunk_metadata,
                "date": analisis["fecha"],
                # "emotions": analisis.get("emotions", []),
                # "topics": analisis.get("topics", []),
                # "intensity": analisis.get("intensity"),
                # "people": analisis.get("people"),
                # "source": "llm" if "chunks_llm" in locals() else "heuristic"
            }
        }

        chunks_enriquecidos.append(enriched)

    return chunks_enriquecidos



def obtener_archivos_diario(carpeta: str) -> List[Path]:
    """
    Obtiene todos los archivos de diario válidos de una carpeta.
    
    Args:
        carpeta: Ruta a la carpeta con los archivos de diario
        
    Returns:
        Lista de Path objects con los archivos válidos ordenados por fecha
        
    Raises:
        FileReadError: Si la carpeta no existe o no se puede leer
    """
    try:
        ruta_carpeta = Path(carpeta)
        
        if not ruta_carpeta.exists():
            raise FileReadError(f"La carpeta '{carpeta}' no existe")
        
        if not ruta_carpeta.is_dir():
            raise FileReadError(f"'{carpeta}' no es una carpeta válida")
        
        archivos_md = list(ruta_carpeta.glob("*.md"))
        archivos_validos = [
            archivo for archivo in archivos_md
            if validar_nombre_archivo(archivo.name)
        ]
        
        if not archivos_validos:
            logger.warning(f"No se encontraron archivos de diario válidos en '{carpeta}'")
            return []
        
        archivos_validos.sort(key=lambda x: datetime.strptime(
            x.name.replace('.md', ''), '%d-%m-%Y'
        ))
        
        logger.info(f"Encontrados {len(archivos_validos)} archivos de diario en '{carpeta}'")
        return archivos_validos
        
    except PermissionError:
        raise FileReadError(f"Sin permisos para leer la carpeta '{carpeta}'")
    except Exception as e:
        raise FileReadError(f"Error al leer la carpeta: {e}")


def obtener_fechas_procesadas(ruta_json: str = "diario.json") -> Set[str]:
    """
    Obtiene las fechas que ya han sido procesadas del historial.
    
    Args:
        ruta_json: Ruta al archivo JSON del historial
        
    Returns:
        Set con las fechas ya procesadas (formato: dd-mm-yyyy)
    """
    try:
        historial = cargar_historial_diario(ruta_json)
        
        fechas = set()
        for entrada in historial:
            if 'fecha' in entrada:
                fechas.add(entrada['fecha'])
        
        logger.info(f"Encontradas {len(fechas)} entradas ya procesadas")
        return fechas
        
    except Exception as e:
        logger.warning(f"No se pudieron cargar fechas procesadas: {e}")
        return set()


def obtener_archivos_pendientes(
    carpeta: str,
    ruta_json: str = "diario.json"
) -> List[Path]:
    """
    Obtiene los archivos que aún no han sido procesados.
    
    Args:
        carpeta: Carpeta con los archivos de diario
        ruta_json: Archivo JSON con el historial
        
    Returns:
        Lista de archivos pendientes de procesar
    """
    todos_archivos = obtener_archivos_diario(carpeta)
    fechas_procesadas = obtener_fechas_procesadas(ruta_json)
    
    pendientes = [
        archivo for archivo in todos_archivos
        if extraer_fecha_de_nombre(archivo.name) not in fechas_procesadas
    ]
    
    logger.info(f"Archivos pendientes de procesar: {len(pendientes)}")
    return pendientes


def leer_archivo_diario(ruta_archivo: str) -> str:
    """
    Lee el contenido de un archivo de diario.
    
    Args:
        ruta_archivo: Ruta al archivo markdown del diario
        
    Returns:
        Contenido del archivo como string
        
    Raises:
        FileReadError: Si el archivo no existe o no se puede leer
    """
    try:
        archivo = Path(ruta_archivo)
        if not archivo.exists():
            raise FileReadError(f"El archivo '{ruta_archivo}' no existe")
        
        if not archivo.is_file():
            raise FileReadError(f"'{ruta_archivo}' no es un archivo válido")
        
        contenido = archivo.read_text(encoding='utf-8')
        
        if not contenido.strip():
            logger.warning(f"El archivo '{ruta_archivo}' está vacío")
        
        return contenido
        
    except UnicodeDecodeError as e:
        raise FileReadError(f"Error de codificación al leer '{ruta_archivo}': {e}")
    except PermissionError:
        raise FileReadError(f"Sin permisos para leer '{ruta_archivo}'")
    except Exception as e:
        raise FileReadError(f"Error inesperado al leer el archivo: {e}")


def analizar_con_llm(contenido: str, modelo: str = "liquidai/lfm2-2.6b-exp@f16") -> str:
    """
    Analiza el contenido del diario usando LM Studio.
    
    Args:
        contenido: Texto del diario a analizar
        modelo: Identificador del modelo a usar
        
    Returns:
        Respuesta del modelo como string
        
    Raises:
        ModelError: Si hay problemas con el modelo o la conexión
    """
    prompt = f"""
    INSTRUCCIONES:
    Tu tarea es analizar texto de diario personal y extraer información estructurada.
    No hagas juicios, no des consejos, no interpretes más allá del texto.
    No inventes información que no esté explícita o claramente inferida.
    Si algo no está presente, devuélvelo como null.
    
    SALIDA:
    Devuelve exclusivamente un objeto JSON válido con las siguientes claves:
        summary: resumen neutral en máximo 3 líneas
        emotions: lista de emociones explícitas o claramente inferidas
        topics: lista de temas principales
        people: lista de personas mencionadas (o null)
        intensity: "baja", "media" o "alta"
    
    TEXTO DEL DIARIO:
    <<<{contenido}>>>"""
    

    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": "Eres un analizador de diarios personales."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = post_with_retry(
            GROQ_API_URL,
            payload,
            headers
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        raise ModelError(f"Error al procesar con API: {e}")

    # try:
    #     with lms.Client() as client:
    #         model = client.llm.model(modelo)
    #         result = model.respond(prompt)
            
    #         if not result or not hasattr(result, 'content'):
    #             raise ModelError("El modelo no devolvió una respuesta válida")
            
    #         return result.content
            
    # except ConnectionError as e:
    #     raise ModelError(f"No se pudo conectar con LM Studio: {e}")
    # except Exception as e:
    #     raise ModelError(f"Error al procesar con el modelo: {e}")

def chunkear_con_llm(
    texto: str,
    modelo: str = "liquidai/lfm2-2.6b-exp@f16"
) -> List[Dict[str, str]]:
    """
    Usa un LLM para dividir el texto en chunks semánticos conscientes.

    Returns:
        Lista de objetos:
        {
            "index": int,
            "type": "hechos|emociones|reflexion|mixto",
            "text": string
        }
    """
    prompt = f"""
Eres un modelo de lenguaje encargado de procesar entradas de un diario personal.

Tu tarea es:
1. Dividir TODO el texto en CHUNKS SEMÁNTICOS.
2. Cada chunk debe ser coherente, completo y autosuficiente.
3. Enriquecer cada chunk con metadatos SOLO si están explícitamente justificados por el texto del chunk.
4. No inventar información.
5. No asumir contexto externo.
6. No interpretar más allá de lo escrito.

────────────────────────
REGLAS DE CHUNKING (OBLIGATORIAS)
────────────────────────

DEFINICIÓN DE CHUNK:
Un chunk es una unidad narrativa completa que desarrolla UNA idea principal.
Puede incluir varias oraciones o párrafos mientras sigan siendo la misma idea.

OBLIGATORIO:
- TODO el texto original debe quedar cubierto.
- NO omitas ningún fragmento.
- NO reescribas ni resumas el texto.
- El texto del chunk debe ser EXACTAMENTE el original.

TAMAÑO:
- Un chunk NO PUEDE tener menos de 40 palabras.
- Si una oración o párrafo es corto, DEBES fusionarlo con el siguiente relacionado.
- Máximo recomendado: 80–120 palabras.
- Prefiere chunks grandes y coherentes antes que muchos pequeños.

COHERENCIA SEMÁNTICA:
- NO crees un nuevo chunk solo por cambio de línea.
- NO separes listas, presentaciones o descripciones relacionadas.
- Si el texto presenta varias personas dentro de la misma sección narrativa,
  DEBEN permanecer en el mismo chunk.
- Si una idea continúa, DEBE permanecer en el mismo chunk.
- No mezcles ideas claramente distintas en un mismo chunk.

────────────────────────
TIPO DE CHUNK
────────────────────────
Asigna SOLO UNO:
- hechos → descripción de eventos o situaciones
- reflexion → pensamientos, evaluaciones personales
- emociones → expresión emocional clara
- mixto → hechos + reflexión o emoción inseparables

────────────────────────
METADATOS (SOLO SI SON EXPLÍCITOS)
────────────────────────

Incluye metadatos SOLO si el texto lo justifica claramente.

- emotions:
  - Máximo 2
  - SOLO si la emoción está explícitamente expresada en el texto
- topics:
  - Temas directamente mencionados
- people:
  - SOLO nombres que aparecen explícitamente en el texto del chunk
  - NO incluyas categorías genéricas
- intensity:
  - baja | media | alta
  - SOLO si hay carga emocional clara

SI UN DATO NO ES CLARO, NO LO INCLUYAS.
NO infieras.
NO completes campos por obligación.

────────────────────────
SALIDA OBLIGATORIA (FORMATO EXACTO)
────────────────────────

Devuelve SOLO un JSON válido con esta estructura exacta:

{{
  "chunks": [
    {{
      "index": 0,
      "type": "emociones | reflexion | hechos | mixto",
      "text": "texto del chunk",
      "metadata": {{
        "people": []
      }}
    }}
  ]
}}

NO agregues texto fuera del JSON.
NO agregues campos adicionales.

────────────────────────
TEXTO A PROCESAR:
<<<{texto}>>>
"""

    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": "Eres un modelo encargado de chunking semántico estricto."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = post_with_retry(
            GROQ_API_URL,
            payload,
            headers
        )
        response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"]
        logger.debug("Respuesta cruda chunking LLM:\n" + raw)

        json_text = extraer_json_de_respuesta(raw)
        data = json.loads(json_text)

        if "chunks" not in data:
            raise JSONParseError("Respuesta sin chunks")

        return data["chunks"]

    except Exception as e:
        raise ModelError(f"Chunking vía API falló: {e}")

EMOTIONS_WHITELIST = {
    "alegría", "tristeza", "miedo", "enojo",
    "ansiedad", "frustración", "calma", "confusión"
}

def sanitizar_chunk(chunk: Dict[str, Any], texto_chunk: str) -> Dict[str, Any]:
    clean = dict(chunk)

    metadata = clean.get("metadata") or {}
    safe_meta = {}

    # people: solo strings capitalizados presentes en el texto
    if "people" in metadata:
        safe_people = []
        for p in metadata["people"]:
            if isinstance(p, str) and p in texto_chunk:
                safe_people.append(p)
        if safe_people:
            safe_meta["people"] = safe_people

    # emotions: whitelist + presentes literalmente
    if "emotions" in metadata:
        safe_emotions = []
        for e in metadata["emotions"]:
            if (
                isinstance(e, str)
                and e.lower() in EMOTIONS_WHITELIST
                and e.lower() in texto_chunk.lower()
            ):
                safe_emotions.append(e.lower())
        if safe_emotions:
            safe_meta["emotions"] = safe_emotions

    # intensity: solo valores válidos
    if metadata.get("intensity") in {"baja", "media", "alta"}:
        safe_meta["intensity"] = metadata["intensity"]

    clean["metadata"] = safe_meta
    return clean


    # try:
    #     with lms.Client() as client:
    #         model = client.llm.model(modelo)
    #         result = model.respond(prompt)

    #         if not result or not hasattr(result, 'content'):
    #             raise ModelError("Respuesta inválida del modelo en chunking")

    #         # LOG CRÍTICO: respuesta cruda
    #         logger.debug("Respuesta cruda chunking LLM:\n" + result.content)

    #         json_text = extraer_json_de_respuesta(result.content)
    #         data = json.loads(json_text)

    #         if "chunks" not in data or not isinstance(data["chunks"], list):
    #             raise JSONParseError("Estructura inválida de chunks")

    #         return data["chunks"]

    # except Exception as e:
    #     logger.error(f"Chunking con LLM falló: {e}")
    #     raise


def extraer_json_de_respuesta(texto: str) -> str:
    """
    Extrae el bloque JSON de la respuesta del modelo.
    
    Args:
        texto: Respuesta completa del modelo
        
    Returns:
        String JSON limpio
        
    Raises:
        JSONParseError: Si no se encuentra JSON válido
    """
    match = re.search(r'(?s)```(?:json)?\s*(.*?)\s*```', texto)
    
    if match:
        return match.group(1).strip()
    
    match = re.search(r'(?s)\{.*\}', texto)
    if match:
        return match.group(0).strip()
    
    raise JSONParseError("No se encontró un bloque JSON válido en la respuesta del modelo")


def parsear_analisis(json_texto: str, fecha: str) -> Dict[str, Any]:
    """
    Parsea el JSON y valida su estructura.
    
    Args:
        json_texto: String JSON a parsear
        fecha: Fecha del diario en formato dd-mm-yyyy
        
    Returns:
        Diccionario con los datos parseados
        
    Raises:
        JSONParseError: Si el JSON es inválido o no tiene la estructura esperada
    """
    try:
        datos = json.loads(json_texto)
    except json.JSONDecodeError as e:
        raise JSONParseError(f"JSON inválido: {e}")
    
    datos['fecha'] = fecha
    
    campos_requeridos = {'summary', 'emotions', 'topics', 'people', 'intensity'}
    campos_faltantes = campos_requeridos - set(datos.keys())
    
    if campos_faltantes:
        logger.warning(f"Campos faltantes en el análisis: {campos_faltantes}")
    
    if 'intensity' in datos and datos['intensity'] not in ['baja', 'media', 'alta', None]:
        logger.warning(f"Valor de intensity inválido: {datos['intensity']}")
    
    return datos


def cargar_historial_diario(ruta_json: str = "diario.json") -> list:
    """
    Carga el historial existente del diario.
    
    Args:
        ruta_json: Ruta al archivo JSON del historial
        
    Returns:
        Lista con las entradas previas
        
    Raises:
        JSONParseError: Si el archivo existe pero no es JSON válido
    """
    archivo = Path(ruta_json)
    
    if not archivo.exists():
        logger.info(f"Creando nuevo archivo de historial: {ruta_json}")
        return []
    
    try:
        contenido = archivo.read_text(encoding='utf-8')
        if not contenido.strip():
            logger.warning(f"El archivo {ruta_json} está vacío, iniciando lista nueva")
            return []
        
        datos = json.loads(contenido)
        
        if not isinstance(datos, list):
            raise JSONParseError(f"El archivo {ruta_json} no contiene una lista")
        
        return datos
        
    except json.JSONDecodeError as e:
        raise JSONParseError(f"Error al parsear {ruta_json}: {e}")
    except Exception as e:
        raise FileReadError(f"Error al leer {ruta_json}: {e}")


def guardar_analisis(analisis: Dict[str, Any], ruta_json: str = "diario.json") -> None:
    """
    Guarda el análisis en el archivo JSON del historial.
    
    Args:
        analisis: Diccionario con el análisis a guardar
        ruta_json: Ruta al archivo JSON del historial
        
    Raises:
        FileReadError: Si no se puede escribir el archivo
    """
    try:
        historial = cargar_historial_diario(ruta_json)
        historial.append(analisis)
        
        archivo = Path(ruta_json)
        archivo.write_text(
            json.dumps(historial, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        logger.info(f"Análisis guardado exitosamente en {ruta_json}")
        
    except PermissionError:
        raise FileReadError(f"Sin permisos para escribir en {ruta_json}")
    except Exception as e:
        raise FileReadError(f"Error al guardar el análisis: {e}")


def guardar_chunks(chunks: List[Dict[str, Any]], ruta_json: str = "diario_chunks.json") -> None:
    """
    Guarda los chunks en un archivo JSON separado.
    
    Args:
        chunks: Lista de chunks a guardar
        ruta_json: Ruta al archivo JSON de chunks
        
    Raises:
        FileReadError: Si no se puede escribir el archivo
    """
    try:
        archivo = Path(ruta_json)
        
        # Cargar chunks existentes si el archivo existe
        chunks_existentes = []
        if archivo.exists():
            try:
                contenido = archivo.read_text(encoding='utf-8')
                if contenido.strip():
                    chunks_existentes = json.loads(contenido)
            except:
                logger.warning(f"No se pudieron cargar chunks existentes, creando nuevo archivo")
        
        # Agregar nuevos chunks
        chunks_existentes.extend(chunks)
        
        # Guardar
        archivo.write_text(
            json.dumps(chunks_existentes, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        logger.info(f"Chunks guardados exitosamente en {ruta_json} (total: {len(chunks_existentes)})")
        
    except PermissionError:
        raise FileReadError(f"Sin permisos para escribir en {ruta_json}")
    except Exception as e:
        raise FileReadError(f"Error al guardar chunks: {e}")


def analizar_diario_individual(
    ruta_archivo: Path,
    ruta_salida: str = "diario.json",
    ruta_chunks: str = "diario_chunks.json",
    modelo: str = "liquidai/lfm2-2.6b-exp@f16",
    generar_chunks: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Analiza un archivo individual de diario.
    
    Args:
        ruta_archivo: Path al archivo de diario
        ruta_salida: Ruta al archivo JSON de salida
        ruta_chunks: Ruta al archivo JSON de chunks
        modelo: Modelo de LM Studio a usar
        generar_chunks: Si True, genera y guarda chunks semánticos
        
    Returns:
        Diccionario con el análisis si fue exitoso, None si hubo error
    """
    try:
        fecha = extraer_fecha_de_nombre(ruta_archivo.name)
        if not fecha:
            logger.error(f"No se pudo extraer fecha válida de '{ruta_archivo.name}'")
            return None
        
        entry_id = generar_id_entrada(fecha)
        logger.info(f"Analizando: {ruta_archivo.name} ({entry_id})")
        
        # 1. Leer archivo
        contenido = leer_archivo_diario(str(ruta_archivo))
        
        # 2. Analizar con LLM
        respuesta = analizar_con_llm(contenido, modelo)
        
        # 3. Extraer JSON
        json_texto = extraer_json_de_respuesta(respuesta)
        
        # 4. Parsear y validar
        analisis = parsear_analisis(json_texto, fecha)
        
        # 5. Agregar información adicional
        analisis['id'] = entry_id
        analisis['raw_text'] = contenido
        analisis['word_count'] = len(contenido.split())
        analisis['char_count'] = len(contenido)

        time.sleep(0.5)

        # 6. Generar chunks si está habilitado
        if generar_chunks:
            chunks = crear_chunks_enriquecidos(
                contenido,
                analisis,
                entry_id,
                modelo
            )
            guardar_chunks(chunks, ruta_chunks)
            analisis['chunk_count'] = len(chunks)
            logger.info(f"✓ Generados {len(chunks)} chunks para {entry_id}")
        
        # 7. Guardar análisis principal
        guardar_analisis(analisis, ruta_salida)
        
        logger.info(f"✓ {ruta_archivo.name} procesado exitosamente")
        return analisis
        
    except DiaryAnalyzerError as e:
        logger.error(f"✗ Error al analizar {ruta_archivo.name}: {e}")
        return None
    except Exception as e:
        logger.error(f"✗ Error inesperado en {ruta_archivo.name}: {e}", exc_info=True)
        return None


def procesar_carpeta_diarios(
    carpeta: str = "diarios",
    ruta_salida: str = "diario.json",
    ruta_chunks: str = "diario_chunks.json",
    modelo: str = "liquidai/lfm2-2.6b-exp@f16",
    forzar_reprocesar: bool = False,
    generar_chunks: bool = True
) -> Dict[str, int]:
    """
    Procesa todos los archivos de diario en una carpeta.
    
    Args:
        carpeta: Carpeta con los archivos de diario
        ruta_salida: Archivo JSON donde guardar los análisis
        ruta_chunks: Archivo JSON donde guardar los chunks
        modelo: Modelo de LM Studio a usar
        forzar_reprocesar: Si True, reprocesa todos los archivos
        generar_chunks: Si True, genera chunks semánticos
        
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    logger.info("="*60)
    logger.info("INICIANDO PROCESAMIENTO BATCH DE DIARIOS")
    if generar_chunks:
        logger.info("Modo: CON CHUNKING SEMÁNTICO")
    logger.info("="*60)
    
    estadisticas = {
        'total': 0,
        'exitosos': 0,
        'fallidos': 0,
        'omitidos': 0,
        'chunks_generados': 0
    }
    
    try:
        if forzar_reprocesar:
            archivos = obtener_archivos_diario(carpeta)
            logger.info("Modo: REPROCESAR TODO")
        else:
            archivos = obtener_archivos_pendientes(carpeta, ruta_salida)
            logger.info("Modo: SOLO NUEVOS")
        
        estadisticas['total'] = len(archivos)
        
        if not archivos:
            logger.info("No hay archivos para procesar")
            return estadisticas
        
        logger.info(f"Archivos a procesar: {estadisticas['total']}")
        logger.info("-"*60)
        
        for i, archivo in enumerate(archivos, 1):
            logger.info(f"\n[{i}/{estadisticas['total']}] Procesando...")
            
            resultado = analizar_diario_individual(
                archivo, 
                ruta_salida, 
                ruta_chunks,
                modelo,
                generar_chunks
            )
            
            if resultado:
                estadisticas['exitosos'] += 1
                if generar_chunks and 'chunk_count' in resultado:
                    estadisticas['chunks_generados'] += resultado['chunk_count']
            else:
                estadisticas['fallidos'] += 1
            
            if i < len(archivos):
                logger.info("Esperando 1 segundo antes del siguiente archivo...")
                import time
                time.sleep(1)
        
        # Resumen final
        logger.info("\n" + "="*60)
        logger.info("RESUMEN DEL PROCESAMIENTO")
        logger.info("="*60)
        logger.info(f"Total de archivos: {estadisticas['total']}")
        logger.info(f"✓ Exitosos: {estadisticas['exitosos']}")
        logger.info(f"✗ Fallidos: {estadisticas['fallidos']}")
        logger.info(f"⊘ Omitidos: {estadisticas['omitidos']}")
        if generar_chunks:
            logger.info(f"📦 Chunks generados: {estadisticas['chunks_generados']}")
        
        if estadisticas['exitosos'] == estadisticas['total']:
            logger.info("\n🎉 ¡Todos los archivos procesados exitosamente!")
        elif estadisticas['fallidos'] > 0:
            logger.warning(f"\n⚠️  {estadisticas['fallidos']} archivo(s) con errores")
        
        return estadisticas
        
    except DiaryAnalyzerError as e:
        logger.error(f"Error en el procesamiento batch: {e}")
        return estadisticas
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return estadisticas


if __name__ == "__main__":
    # Configuración
    CARPETA_DIARIOS = "diarios"              # Carpeta con los archivos .md
    ARCHIVO_SALIDA = "data/diario.json"           # Archivo JSON de análisis
    ARCHIVO_CHUNKS = "data/diario_chunks.json"    # Archivo JSON de chunks
    MODELO_LLM = "qwen/qwen3-32b"
    MODELO_LLM_local = "lmstudio-community/Qwen2.5-7B-Instruct-1M-GGUF" #"liquidai/lfm2-2.6b-exp@f16"
    FORZAR_REPROCESAR = False                # True para reprocesar todo
    GENERAR_CHUNKS = True                    # True para generar chunks semánticos
    
    # Ejecutar procesamiento batch
    estadisticas = procesar_carpeta_diarios(
        carpeta=CARPETA_DIARIOS,
        ruta_salida=ARCHIVO_SALIDA,
        ruta_chunks=ARCHIVO_CHUNKS,
        modelo=MODELO_LLM,
        forzar_reprocesar=FORZAR_REPROCESAR,
        generar_chunks=GENERAR_CHUNKS
    )
    
    # Mensaje final
    print("\n" + "="*60)
    if estadisticas['exitosos'] > 0:
        print(f"✓ Procesamiento completado: {estadisticas['exitosos']} archivos analizados")
        if estadisticas['chunks_generados'] > 0:
            print(f"📦 Total de chunks generados: {estadisticas['chunks_generados']}")
    else:
        print("✗ No se pudo procesar ningún archivo")
    print("="*60)