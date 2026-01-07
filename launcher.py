import uvicorn
import webbrowser
import threading
import time
import os
import sys
from backend.app.main import app

def open_browser():
    """Espera un momento a que el servidor inicie y abre el navegador."""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")

def initialize_app():
    """Asegura que los directorios necesarios existan."""
    print("🚀 Iniciando Diario IA...")
    dirs = [
        "data/diary/entries",
        "data/diary/processed",
        "data/raw"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

if __name__ == "__main__":
    initialize_app()
    
    # Iniciar el navegador en un hilo separado
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar el servidor
    # Nota: reload=False es necesario para que funcione con PyInstaller
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
