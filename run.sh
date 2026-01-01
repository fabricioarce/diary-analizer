#!/usr/bin/env bash
set -e

echo "=============================================="
echo "📔 Diario IA — Pipeline completo"
echo "=============================================="

# -------------------------
# Comprobaciones básicas
# -------------------------
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 no está instalado"
  exit 1
fi

# -------------------------
# Entorno virtual
# -------------------------
if [ ! -d ".venv" ]; then
  echo "🔧 Creando entorno virtual..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# -------------------------
# Dependencias
# -------------------------
if [ -f "requirements.txt" ]; then
  echo "📦 Instalando dependencias..."
  pip install --quiet -r requirements.txt
fi

# -------------------------
# Estructura mínima
# -------------------------
mkdir -p diarios data

# =========================
# 1. Análisis del diario
# =========================
echo ""
echo "🧠 [1/4] Analizando entradas del diario..."
python diary_analyzer.py

sleep 5
# =========================
# 2. Generación de embeddings
# =========================
echo ""
echo "🧩 [2/4] Generando embeddings..."
python embedding_generator.py

sleep 5
# =========================
# 3. Actualización FAISS
# =========================
echo ""
echo "📦 [3/4] Actualizando índice vectorial..."
python query_engine.py --build-index

sleep 5
# =========================
# 4. Chat RAG activo
# =========================
echo "¿Cómo quieres usar el sistema?"
echo "1) Interfaz gráfica"
echo "2) Chat por terminal"
read -p "> " opcion

if [ "$opcion" == "1" ]; then
  streamlit run app.py
else
  python rag_chat_engine.py
fi