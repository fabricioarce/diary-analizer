import json
import logging
from datetime import date
from pathlib import Path
from backend.app.config import CHUNKS_FILE, FAISS_INDEX_FILE, METADATA_FILE, RAW_DIARY_JSON
from backend.app.core.diary_analyzer import (
    analizar_con_llm, 
    crear_chunks_enriquecidos, 
    generar_id_entrada,
    extraer_json_de_respuesta,
    guardar_analisis
)
from backend.app.core.embedding_generator import DiarioVectorIndexer

logger = logging.getLogger(__name__)

DIARY_PATH = Path("data/diary/entries")
DIARY_PATH.mkdir(parents=True, exist_ok=True)

def save_entry(text: str, date_str: str = None) -> str:
    if date_str:
        # User defined date
        save_date = date_str
    else:
        # Default to today
        save_date = date.today().isoformat()
        
    path = DIARY_PATH / f"{save_date}.md"
    path.write_text(text, encoding="utf-8")
    return save_date

def process_diary_entry(text: str, date_str: str):
    """
    Background task to analyze, chunk, and index the new entry.
    """
    logger.info(f"Processing diary entry for {date_str}...")
    
    try:
        # 1. Analyze
        logger.info("Running LLM analysis...")
        analisis_raw = analizar_con_llm(text)
        
        # Try to parse JSON, handling potential markdown blocks
        try:
             analisis = json.loads(analisis_raw)
        except json.JSONDecodeError:
             from backend.app.core.diary_analyzer import extraer_json_de_respuesta
             json_text = extraer_json_de_respuesta(analisis_raw)
             analisis = json.loads(json_text)

        # 2. Enrich Analysis
        # Adjust date format for ID generation: YYYY-MM-DD -> DD-MM-YYYY
        y, m, d = date_str.split("-")
        date_formatted = f"{d}-{m}-{y}"
        entry_id = generar_id_entrada(date_formatted)

        analisis["fecha"] = date_str
        analisis['id'] = entry_id
        analisis['raw_text'] = text
        analisis['word_count'] = len(text.split())
        analisis['char_count'] = len(text)
        
        # 3. Chunk
        logger.info("Creating enriched chunks...")
        new_chunks = crear_chunks_enriquecidos(text, analisis, entry_id)
        analisis['chunk_count'] = len(new_chunks)

        # 4. Save to Raw History (diario.json)
        logger.info(f"Saving analysis to {RAW_DIARY_JSON}...")
        guardar_analisis(analisis, RAW_DIARY_JSON)
        
        # 5. Update Chunks File
        logger.info("Updating chunks file...")
        all_chunks = []
        if CHUNKS_FILE.exists():
            try:
                with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                    all_chunks = json.load(f)
            except Exception as e:
                logger.error(f"Error reading existing chunks: {e}")
        
        # Append new chunks
        all_chunks.extend(new_chunks)
        
        # Ensure directory exists
        CHUNKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
            
        # 6. Re-Index
        logger.info("Re-indexing FAISS...")
        indexer = DiarioVectorIndexer()
        indexer.indexar_desde_chunks(CHUNKS_FILE, FAISS_INDEX_FILE, METADATA_FILE)
        
        logger.info(f"Successfully processed entry for {date_str}")
        
    except Exception as e:
        logger.error(f"Error processing diary entry: {e}", exc_info=True)

def list_entries():
    return sorted(p.stem for p in DIARY_PATH.glob("*.md"))

def read_entry(date: str):
    path = DIARY_PATH / f"{date}.md"
    if not path.exists():
        return None
    return {"date": date, "text": path.read_text(encoding="utf-8")}
