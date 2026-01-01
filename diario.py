"""
Analizador de Diario Personal con Chunking Inteligente por LLM
---------------------------------------------------------------
Script para analizar entradas de diario usando LM Studio.
Usa el modelo de lenguaje para dividir inteligentemente el texto en chunks semánticos.

Uso:
    python diary_analyzer.py

Requisitos:
    - lmstudio
    - Python 3.7+
"""

import re
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any, List, Set
from datetime import datetime
import lmstudio as lms


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Prompt para chunking semántico con LLM
PROMPT_CHUNKING = """INSTRUCCIONES:
Divide el texto del diario en fragmentos semánticos coherentes.

REGLAS IMPORTANTES:
1. Cada fragmento debe representar UNA idea completa
2. NO repitas texto entre fragmentos
3. NO resumas - conserva el texto original EXACTAMENTE como está
4. Si un párrafo tiene múltiples ideas distintas, divídelo
5. Si varios párrafos hablan de lo mismo, pueden ir juntos
6. Mínimo 50 palabras por fragmento (excepto si es una idea muy corta)
7. Máximo 300 palabras por fragmento

TIPOS DE FRAGMENTOS:
- "hechos": Eventos, acciones, actividades realizadas
- "emociones": Sentimientos, estados emocionales explícitos
- "reflexion": Pensamientos, aprendizajes, introspección, análisis
- "intencion": Planes, metas, propósitos, deseos futuros
- "mixto": Combinación de varios tipos en una misma idea

SALIDA:
Devuelve SOLO un objeto JSON válido (sin markdown, sin explicaciones) con esta estructura:
{{
  "chunks": [
    {{
      "type": "hechos",
      "text": "texto original del fragmento..."
    }}
  ]
}}

TEXTO DEL DIARIO:
<<<
{contenido}
>>>"""


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


def validar_chunks(chunks: List[Dict[str, str]], texto_original: str) -> bool:
    """
    Valida que los chunks generados sean correctos.
    
    Args:
        chunks: Lista de chunks a validar
        texto_original: Texto original del diario
        
    Returns:
        True si los chunks son válidos
    """
    if not chunks:
        logger.warning("No hay chunks para validar")
        return False
    
    # 1. Verificar tipos válidos
    tipos_validos = {'hechos', 'emociones', 'reflexion', 'intencion', 'mixto'}
    for i, chunk in enumerate(chunks):
        if chunk.get('type') not in tipos_validos:
            logger.warning(f"Chunk {i} tiene tipo inválido: {chunk.get('type')}")
            return False
        
        if not chunk.get('text', '').strip():
            logger.warning(f"Chunk {i} tiene texto vacío")
            return False
    
    # 2. Verificar cobertura del texto original (al menos 80%)
    texto_chunks = ' '.join([c['text'] for c in chunks])
    palabras_original = set(texto_original.lower().split())
    palabras_chunks = set(texto_chunks.lower().split())
    
    if palabras_original:
        cobertura = len(palabras_original & palabras_chunks) / len(palabras_original)
        if cobertura < 0.8:
            logger.warning(f"Chunks solo cubren {cobertura:.1%} del texto original")
            return False
    
    return True


def generar_chunks_con_llm(
    texto: str,
    modelo: str = "liquidai/lfm2-2.6b-exp@f16",
    max_intentos: int = 2
) -> List[Dict[str, str]]:
    """
    Genera chunks usando el LLM para división semántica inteligente.
    
    Args:
        texto: Texto completo del diario
        modelo: Modelo LLM a usar
        max_intentos: Cantidad máxima de reintentos
        
    Returns:
        Lista de chunks con type y text
    """
    logger.info("Generando chunks con LLM...")
    
    for intento in range(max_intentos):
        try:
            # 1. Construir prompt
            prompt = PROMPT_CHUNKING.format(contenido=texto)
            
            # 2. Llamar al LLM
            with lms.Client() as client:
                model = client.llm.model(modelo)
                result = model.respond(prompt)
                respuesta = result.content
            
            # 3. Extraer JSON
            json_texto = extraer_json_de_respuesta(respuesta)
            
            # 4. Parsear
            data = json.loads(json_texto)
            
            # 5. Validar estructura
            if 'chunks' not in data:
                raise ValueError("Respuesta no contiene 'chunks'")
            
            chunks = data['chunks']
            
            if not isinstance(chunks, list):
                raise ValueError("'chunks' debe ser una lista")
            
            # 6. Validar cada chunk
            for i, chunk in enumerate(chunks):
                if 'type' not in chunk or 'text' not in chunk:
                    logger.warning(f"Chunk {i} sin type o text, ajustando...")
                    chunk.setdefault('type', 'mixto')
                    chunk.setdefault('text', '')
            
            # 7. Validar calidad de chunks
            if validar_chunks(chunks, texto):
                logger.info(f"✓ Generados {len(chunks)} chunks válidos por LLM")
                return chunks
            else:
                logger.warning(f"Intento {intento + 1}: chunks inválidos, reintentando...")
                
        except Exception as e:
            logger.error(f"Intento {intento + 1} falló al generar chunks: {e}")
            if intento < max_intentos - 1:
                logger.info("Reintentando...")
                time.sleep(1)
    
    # Fallback: devolver texto completo como un chunk
    logger.warning("Usando fallback: texto completo como un solo chunk")
    return [{
        'type': 'mixto',
        'text': texto
    }]


def crear_chunks_enriquecidos(
    texto: str,
    analisis: Dict[str, Any],
    entry_id: str,
    modelo: str = "liquidai/lfm2-2.6b-exp@f16"
) -> List[Dict[str, Any]]:
    """
    Crea chunks semánticos usando LLM y los enriquece con metadata.
    
    Args:
        texto: Texto completo de la entrada
        analisis: Análisis estructurado de la entrada
        entry_id: ID de la entrada padre
        modelo: Modelo LLM para chunking
        
    Returns:
        Lista de chunks enriquecidos con metadata
    """
    # 1. Generar chunks con LLM
    chunks_llm = generar_chunks_con_llm(texto, modelo)
    
    # 2. Enriquecer con metadata
    chunks_enriquecidos = []
    
    for idx, chunk_data in enumerate(chunks_llm):
        chunk = {
            'chunk_id': generar_id_chunk(entry_id, idx),
            'entry_id': entry_id,
            'index': idx,
            'text': chunk_data['text'],
            'word_count': len(chunk_data['text'].split()),
            'char_count': len(chunk_data['text']),
            'type': chunk_data['type'],
            'metadata': {
                'date': analisis['fecha'],
                'emotions': analisis.get('emotions', []),
                'topics': analisis.get('topics', []),
                'intensity': analisis.get('intensity', 'media'),
                'people': analisis.get('people')
            }
        }
        
        chunks_enriquecidos.append(chunk)
    
    logger.info(f"Creados {len(chunks_enriquecidos)} chunks enriquecidos para {entry_id}")
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
    
    try:
        with lms.Client() as client:
            model = client.llm.model(modelo)
            result = model.respond(prompt)
            
            if not result or not hasattr(result, 'content'):
                raise ModelError("El modelo no devolvió una respuesta válida")
            
            return result.content
            
    except ConnectionError as e:
        raise ModelError(f"No se pudo conectar con LM Studio: {e}")
    except Exception as e:
        raise ModelError(f"Error al procesar con el modelo: {e}")


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
    # Estrategia 1: Buscar bloque de código JSON
    match = re.search(r'(?s)```(?:json)?\s*(.*?)\s*```', texto)
    if match:
        return match.group(1).strip()
    
    # Estrategia 2: Buscar objeto JSON directamente
    match = re.search(r'(?s)\{.*\}', texto)
    if match:
        return match.group(0).strip()
    
    # Estrategia 3: El texto completo podría ser JSON
    texto_limpio = texto.strip()
    if texto_limpio.startswith('{') and texto_limpio.endswith('}'):
        return texto_limpio
    
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
    modelo_analisis: str = "liquidai/lfm2-2.6b-exp@f16",
    modelo_chunking: str = "liquidai/lfm2-2.6b-exp@f16",
    generar_chunks: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Analiza un archivo individual de diario.
    
    Args:
        ruta_archivo: Path al archivo de diario
        ruta_salida: Ruta al archivo JSON de salida
        ruta_chunks: Ruta al archivo JSON de chunks
        modelo_analisis: Modelo para análisis general
        modelo_chunking: Modelo para generar chunks
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
        respuesta = analizar_con_llm(contenido, modelo_analisis)
        
        # 3. Extraer JSON
        json_texto = extraer_json_de_respuesta(respuesta)
        
        # 4. Parsear y validar
        analisis = parsear_analisis(json_texto, fecha)
        
        # 5. Agregar información adicional
        analisis['id'] = entry_id
        analisis['raw_text'] = contenido
        analisis['word_count'] = len(contenido.split())
        analisis['char_count'] = len(contenido)
        
        # 6. Generar chunks si está habilitado
        if generar_chunks:
            chunks = crear_chunks_enriquecidos(contenido, analisis, entry_id, modelo_chunking)
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
    modelo_analisis: str = "liquidai/lfm2-2.6b-exp@f16",
    modelo_chunking: str = "liquidai/lfm2-2.6b-exp@f16",
    forzar_reprocesar: bool = False,
    generar_chunks: bool = True
) -> Dict[str, int]:
    """
    Procesa todos los archivos de diario en una carpeta.
    
    Args:
        carpeta: Carpeta con los archivos de diario
        ruta_salida: Archivo JSON donde guardar los análisis
        ruta_chunks: Archivo JSON donde guardar los chunks
        modelo_analisis: Modelo para análisis general
        modelo_chunking: Modelo para generar chunks (puede ser el mismo o diferente)
        forzar_reprocesar: Si True, reprocesa todos los archivos
        generar_chunks: Si True, genera chunks semánticos con LLM
        
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    logger.info("="*60)
    logger.info("INICIANDO PROCESAMIENTO BATCH DE DIARIOS")
    if generar_chunks:
        logger.info("Modo: CON CHUNKING SEMÁNTICO (LLM)")
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
                modelo_analisis,
                modelo_chunking,
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
    ARCHIVO_SALIDA = "diario.json"           # Archivo JSON de análisis
    ARCHIVO_CHUNKS = "diario_chunks.json"    # Archivo JSON de chunks

    # Uso modelo
    MODELO_ANALISIS = "liquidai/lfm2-2.6b-exp@f16"  # Para análisis rápido
    MODELO_CHUNKING = "mistral-7b-instruct"         # Para chunking preciso
    FORZAR_REPROCESAR = False                # True para reprocesar todo
    GENERAR_CHUNKS = True                    # True para generar chunks semánticos
    USAR_LLM_CHUNKING = True  # Tu método
    
    # Ejecutar procesamiento batch
    estadisticas = procesar_carpeta_diarios(
        carpeta=CARPETA_DIARIOS,
        ruta_salida=ARCHIVO_SALIDA,
        ruta_chunks=ARCHIVO_CHUNKS,
        modelo_analisis= MODELO_ANALISIS,
        modelo_chunking= MODELO_CHUNKING,
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