from backend.app.modules.journal.core.rag_chat_engine_api import DiarioRAGChat

_chat = DiarioRAGChat()

def ask_chat(question: str) -> str:
    return _chat.preguntar(question)
