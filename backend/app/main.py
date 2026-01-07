from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.app.api import diary, chat, stats
from backend.app.core.exceptions import global_exception_handler

app = FastAPI(title="Diario Reflexivo API")

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(diary.router, prefix="/api/diary")
app.include_router(chat.router, prefix="/api/chat")
app.include_router(stats.router, prefix="/api/stats")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir el frontend compilado
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")