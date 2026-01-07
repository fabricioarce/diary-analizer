from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from backend.app.services.diary_service import (
    save_entry,
    list_entries,
    read_entry,
    process_diary_entry
)

router = APIRouter()

class DiaryEntry(BaseModel):
    text: str
    date: str = None

@router.post("/save")
def save_diary(entry: DiaryEntry, background_tasks: BackgroundTasks):
    date_str = save_entry(entry.text, entry.date)
    background_tasks.add_task(process_diary_entry, entry.text, date_str)
    return {"status": "ok", "message": "Entry saved and processing started"}

@router.get("/list")
def list_diary():
    return list_entries()

@router.get("/{date}")
def get_diary(date: str):
    entry = read_entry(date)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry
