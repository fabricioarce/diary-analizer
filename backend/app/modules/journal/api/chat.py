from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.modules.journal.services.chat_service import ask_chat

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("")
def chat(req: ChatRequest):
    return {"answer": ask_chat(req.question)}
