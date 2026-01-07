import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Adjust path to import from backend
sys.path.append(os.getcwd())

from sqlmodel import Session, select
from backend.app.core.database import engine, init_db
from backend.app.modules.journal.models import JournalEntry, EntryAnalysis, EntryChunk
from backend.app.config import DIARY_ENTRIES_DIR, RAW_DIARY_JSON, CHUNKS_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    init_db()
    
    with Session(engine) as session:
        # 1. Load basic entries from Markdown
        logger.info(f"Loading entries from {DIARY_ENTRIES_DIR}...")
        md_files = list(DIARY_ENTRIES_DIR.glob("*.md"))
        
        for md_file in md_files:
            try:
                date_str = md_file.stem
                # Expecting YYYY-MM-DD
                try:
                    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    # Fallback for DD-MM-YYYY if any
                    entry_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                
                # Check if already exists
                existing = session.exec(select(JournalEntry).where(JournalEntry.date == entry_date)).first()
                if existing:
                    continue
                
                content = md_file.read_text(encoding="utf-8")
                entry = JournalEntry(
                    date=entry_date,
                    raw_text=content,
                    word_count=len(content.split()),
                    char_count=len(content)
                )
                session.add(entry)
                logger.info(f"Added entry for {entry_date}")
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        session.commit()
        
        # 2. Load analysis from diario.json
        if RAW_DIARY_JSON.exists():
            logger.info(f"Loading analysis from {RAW_DIARY_JSON}...")
            with open(RAW_DIARY_JSON, "r", encoding="utf-8") as f:
                historial = json.load(f)
            
            for item in historial:
                try:
                    date_str = item.get("fecha")
                    if not date_str: continue
                    
                    try:
                        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        entry_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                        
                    entry = session.exec(select(JournalEntry).where(JournalEntry.date == entry_date)).first()
                    if not entry:
                        logger.warning(f"Entry for analysis {date_str} not found in DB, skipping analysis migration.")
                        continue
                    
                    # Refresh to get ID
                    session.refresh(entry)
                    
                    # Check if analysis exists
                    existing_analysis = session.exec(select(EntryAnalysis).where(EntryAnalysis.entry_id == entry.id)).first()
                    if existing_analysis:
                        continue
                        
                    analysis = EntryAnalysis(
                        entry_id=entry.id,
                        summary=item.get("summary", ""),
                        intensity=item.get("intensity", "media"),
                        emotions=item.get("emotions", []),
                        topics=item.get("topics", []),
                        people=item.get("people", [])
                    )
                    session.add(analysis)
                    logger.info(f"Added analysis for {entry_date}")
                except Exception as e:
                    logger.error(f"Error processing analysis for {item.get('fecha')}: {e}")
        
        session.commit()
        
        # 3. Load chunks from chunks.json
        if CHUNKS_FILE.exists():
            logger.info(f"Loading chunks from {CHUNKS_FILE}...")
            with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                chunks_data = json.load(f)
            
            for c in chunks_data:
                try:
                    date_str = c.get("metadata", {}).get("date")
                    if not date_str:
                        eid = c.get("entry_id", "")
                        if eid.startswith("entry_"):
                            parts = eid.split("_")
                            if len(parts) >= 4:
                                date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
                
                    if not date_str: continue
                    
                    try:
                        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        entry_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                        
                    entry = session.exec(select(JournalEntry).where(JournalEntry.date == entry_date)).first()
                    if not entry:
                        continue
                    
                    session.refresh(entry)
                    
                    existing_chunk = session.exec(select(EntryChunk).where(EntryChunk.entry_id == entry.id, EntryChunk.index == c.get("index"))).first()
                    if existing_chunk:
                        continue
                        
                    chunk = EntryChunk(
                        entry_id=entry.id,
                        index=c.get("index", 0),
                        chunk_type=c.get("type", "mixto"),
                        text=c.get("text", ""),
                        word_count=c.get("word_count", 0),
                        char_count=c.get("char_count", 0),
                        metadata_json=c.get("metadata", {})
                    )
                    session.add(chunk)
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
        
        session.commit()
        logger.info("Migration completed.")

if __name__ == "__main__":
    migrate()
