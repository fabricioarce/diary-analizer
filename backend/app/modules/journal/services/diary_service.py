import json
import logging
from datetime import date as dt_date, datetime
from pathlib import Path
from typing import List, Optional

from sqlmodel import Session, select
from backend.app.core.database import engine
from backend.app.modules.journal.models import JournalEntry, EntryAnalysis, EntryChunk
from backend.app.config import CHUNKS_FILE, FAISS_INDEX_FILE, METADATA_FILE, RAW_DIARY_JSON, DIARY_ENTRIES_DIR
from backend.app.modules.journal.core.diary_analyzer import (
    analizar_con_llm, 
    crear_chunks_enriquecidos, 
    generar_id_entrada,
    extraer_json_de_respuesta,
    guardar_analisis
)
from backend.app.modules.journal.core.embedding_generator import DiarioVectorIndexer

logger = logging.getLogger(__name__)

def save_entry(text: str, date_str: str = None) -> str:
    if date_str:
        save_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        save_date = dt_date.today()
        
    with Session(engine) as session:
        # Check if entry already exists
        existing = session.exec(select(JournalEntry).where(JournalEntry.date == save_date)).first()
        if existing:
            existing.raw_text = text
            existing.word_count = len(text.split())
            existing.char_count = len(text)
            session.add(existing)
        else:
            entry = JournalEntry(
                date=save_date,
                raw_text=text,
                word_count=len(text.split()),
                char_count=len(text)
            )
            session.add(entry)
        
        session.commit()
        
        # Keep Markdown file as backup for now (optional, but requested by user indirectly by saying "now use sqlite instead of json")
        # I'll keep it for safety during migration phase
        path = DIARY_ENTRIES_DIR / f"{save_date.isoformat()}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        
    return save_date.isoformat()

def process_diary_entry(text: str, date_str: str):
    """
    Background task to analyze, chunk, and index the new entry.
    """
    logger.info(f"Processing diary entry for {date_str}...")
    
    try:
        # 1. Analyze
        logger.info("Running LLM analysis...")
        analisis_raw = analizar_con_llm(text)
        
        try:
             analisis = json.loads(analisis_raw)
        except json.JSONDecodeError:
             from backend.app.modules.journal.core.diary_analyzer import extraer_json_de_respuesta
             json_text = extraer_json_de_respuesta(analisis_raw)
             analisis = json.loads(json_text)

        # 2. Enrich Analysis
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

        # 4. Save to Database
        with Session(engine) as session:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            entry = session.exec(select(JournalEntry).where(JournalEntry.date == entry_date)).first()
            
            if entry:
                # Save Analysis
                existing_analysis = session.exec(select(EntryAnalysis).where(EntryAnalysis.entry_id == entry.id)).first()
                if existing_analysis:
                    session.delete(existing_analysis)
                
                db_analysis = EntryAnalysis(
                    entry_id=entry.id,
                    summary=analisis.get("summary", ""),
                    intensity=analisis.get("intensity", "media"),
                    emotions=analisis.get("emotions", []),
                    topics=analisis.get("topics", []),
                    people=analisis.get("people", [])
                )
                session.add(db_analysis)
                
                # Save Chunks
                # Delete old chunks first
                old_chunks = session.exec(select(EntryChunk).where(EntryChunk.entry_id == entry.id)).all()
                for c in old_chunks:
                    session.delete(c)
                
                for c_data in new_chunks:
                    db_chunk = EntryChunk(
                        entry_id=entry.id,
                        index=c_data.get("index", 0),
                        chunk_type=c_data.get("type", "mixto"),
                        text=c_data.get("text", ""),
                        word_count=c_data.get("word_count", 0),
                        char_count=c_data.get("char_count", 0),
                        metadata_json=c_data.get("metadata", {})
                    )
                    session.add(db_chunk)
                
                session.commit()
                logger.info(f"Database updated for {date_str}")
            else:
                logger.error(f"Entry not found in DB for {date_str} during processing")

        # 4b. Also save to legacy files for compatibility (Optional, but safer for RAG)
        logger.info(f"Saving analysis to {RAW_DIARY_JSON} for compatibility...")
        guardar_analisis(analisis, RAW_DIARY_JSON)
        
        # 5. Update Chunks File (Legacy)
        logger.info("Updating legacy chunks file...")
        all_chunks = []
        if CHUNKS_FILE.exists():
            try:
                with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                    all_chunks = json.load(f)
            except Exception as e:
                logger.error(f"Error reading existing chunks: {e}")
        
        all_chunks.extend(new_chunks)
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
    with Session(engine) as session:
        statement = select(JournalEntry.date).order_by(JournalEntry.date.desc())
        results = session.exec(statement).all()
        return [d.isoformat() for d in results]

def read_entry(date_str: str):
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
        
    with Session(engine) as session:
        entry = session.exec(select(JournalEntry).where(JournalEntry.date == query_date)).first()
        if not entry:
            return None
        return {
            "date": entry.date.isoformat(),
            "text": entry.raw_text,
            "word_count": entry.word_count,
            "char_count": entry.char_count
        }
