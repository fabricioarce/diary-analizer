from datetime import date as dt_date
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON, Column

class JournalEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: dt_date = Field(index=True, unique=True)
    raw_text: str
    word_count: int
    char_count: int
    
    analysis: Optional["EntryAnalysis"] = Relationship(back_populates="entry")
    chunks: List["EntryChunk"] = Relationship(back_populates="entry")

class EntryAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entry_id: int = Field(foreign_key="journalentry.id", index=True, unique=True)
    
    summary: str
    intensity: str  # baja, media, alta
    
    # Using JSON column for lists/dicts to keep it simple while allowing Postgres migration
    emotions: List[str] = Field(sa_column=Column(JSON))
    topics: List[str] = Field(sa_column=Column(JSON))
    people: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    
    entry: JournalEntry = Relationship(back_populates="analysis")

class EntryChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entry_id: int = Field(foreign_key="journalentry.id", index=True)
    
    index: int
    chunk_type: str  # facts, emotions, reflection, mixed
    text: str
    word_count: int
    char_count: int
    
    # Store LLM metadata if any
    metadata_json: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    entry: JournalEntry = Relationship(back_populates="chunks")
