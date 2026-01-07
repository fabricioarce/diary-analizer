import requests
import subprocess
import time
import os
import signal

def test_unified_server():
    print("🧪 Probando servidor unificado...")
    
    # Iniciar el servidor en segundo plano usando launcher.py
    # Usamos uvicorn directamente para controlarlo mejor en el test
    process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "backend.app.main:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Esperar a que inicie
    
    success = False
    try:
        # 1. Probar que la API responde
        api_resp = requests.get("http://127.0.0.1:8000/api/diary/entries")
        print(f"API responde: {api_resp.status_code}")
        
        # 2. Probar que el frontend responde (index.html)
        fe_resp = requests.get("http://127.0.0.1:8000/")
        print(f"Frontend responde: {fe_resp.status_code}")
        
        if api_resp.status_code == 200 and fe_resp.status_code == 200:
            if "dist" in fe_resp.text or "astro" in fe_resp.text.lower():
                print("✅ Verificación exitosa: El servidor sirve API y Frontend.")
                success = True
            else:
                print("⚠️ El frontend respondió pero el contenido no parece ser el de Astro.")
        else:
            print("❌ Error en la respuesta del servidor.")
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
    finally:
        # Matar el proceso
        os.kill(process.pid, signal.SIGTERM)
        
    return success

if __name__ == "__main__":
    if test_unified_server():
        exit(0)
    else:
        exit(1)
