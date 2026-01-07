#!/usr/bin/env bash
set -e

# Configuración de colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}🚀 Nexus Personal OS — Centro de Control Inteligente${NC}"
echo -e "${BLUE}==============================================${NC}"

# 1. Comprobaciones de entorno
check_dependencies() {
    echo -e "${YELLOW}🔍 Comprobando dependencias...${NC}"
    
    # Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 no encontrado."
        exit 1
    fi

    # Entorno Virtual
    if [ ! -d ".venv" ]; then
        echo "🔧 Creando entorno virtual..."
        python3 -m venv .venv
    fi
    source .venv/bin/activate

    # Backend Deps
    echo "📦 Verificando dependencias de Python..."
    pip install -q -r backend/requirements.txt

    # Frontend Deps (Astro)
    if [ -d "frontend" ]; then
        cd frontend
        if command -v pnpm &> /dev/null; then
            MANAGER="pnpm"
        elif command -v npm &> /dev/null; then
            MANAGER="npm"
        else
            echo "⚠️ No se encontró pnpm ni npm para el frontend."
        fi

        if [ ! -z "$MANAGER" ]; then
            if [ ! -d "node_modules" ]; then
                echo "📦 Instalando dependencias de frontend con $MANAGER..."
                $MANAGER install
            fi
        fi
        cd ..
    fi
}

# 2. Pipeline de Procesamiento
run_pipeline() {
    echo -e "\n${BLUE}🧠 Procesando módulos de Nexus (Journal)...${NC}"
    
    mkdir -p data/diary/entries data/diary/processed data/raw
    
    echo "1/3 Analizando archivos..."
    python3 -m backend.app.modules.journal.core.diary_analyzer
    
    echo "2/3 Generando embeddings..."
    python3 -m backend.app.modules.journal.core.embedding_generator
    
    echo "3/3 Actualizando índice vectorial..."
    python3 -m backend.app.modules.journal.core.query_engine --build-index
    
    echo -e "${GREEN}✅ Procesamiento de Journal completado.${NC}"
}

# 3. Lanzamiento de Servicios
start_frontend() {
    echo -e "\n${GREEN}🚀 Lanzando Nexus OS (Dashboard + API)${NC}"
    
    trap "kill 0" EXIT

    # Backend Fastapi
    python3 -m uvicorn backend.app.main:app --reload --port 8000 &
    BACKEND_PID=$!

    # Frontend Astro
    cd frontend && $MANAGER run dev &
    FRONTEND_PID=$!

    wait
}

start_cli() {
    echo -e "\n${GREEN}💬 Iniciando Chat en Terminal (Journal)...${NC}"
    python3 -m backend.app.modules.journal.core.rag_chat_engine_api
}

# --- Menú Principal ---
check_dependencies

echo ""
echo "Selecciona una opción:"
echo "1) 🌐 Full Stack (Procesar + Frontend + Backend)"
echo "2) 💻 CLI Mode (Procesar + Chat por terminal)"
echo "3) 🔄 Solo Actualizar Datos (Para nuevas entradas manuales)"
echo "4) 🛰️ Solo Lanzar Frontend (Sin procesar)"
echo "5) 🗨️ Solo Lanzar CLI (Sin procesar)"
echo "q) Salir"
read -p "> " choice

case $choice in
    1)
        run_pipeline
        start_frontend
        ;;
    2)
        run_pipeline
        start_cli
        ;;
    3)
        run_pipeline
        ;;
    4)
        start_frontend
        ;;
    5)
        start_cli
        ;;
    q)
        exit 0
        ;;
    *)
        echo "Opción no válida."
        ;;
esac