"""
Motor de Consulta Semántica del Diario
-------------------------------------
Busca entradas relevantes en FAISS y construye contexto
para un modelo de lenguaje reflexivo.
"""

import json
import logging
from typing import List, Dict, Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.app.config import FAISS_INDEX_FILE, METADATA_FILE


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


# ============================================================
# CLASE PRINCIPAL
# ============================================================

class DiarioQueryEngine:
    """
    Maneja búsquedas semánticas sobre el diario personal.
    """

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small"
    ):
        logger.info("Inicializando motor de consulta")

        logger.info(f"Cargando modelo de embeddings: {model_name}")
        self.model = SentenceTransformer(
            model_name,
            device="cpu"
        )

        logger.info(f"Cargando índice FAISS: {FAISS_INDEX_FILE}")
        self.index = faiss.read_index(str(FAISS_INDEX_FILE))

        logger.info(f"Cargando metadata: {METADATA_FILE}")
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        logger.info("Motor listo")


    # --------------------------------------------------------

    def _embed_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.astype("float32").reshape(1, -1)

    # --------------------------------------------------------

    def buscar(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        logger.info(f"Buscando chunks relevantes (k={k})")

        query_vec = self._embed_query(query)
        scores, indices = self.index.search(query_vec, k)

        resultados = []
        for rank, idx in enumerate(indices[0]):
            chunk = self.metadata[idx].copy()
            chunk["rank"] = rank + 1
            chunk["score"] = float(scores[0][rank])
            resultados.append(chunk)

        logger.info("Búsqueda completada")
        return resultados

    # --------------------------------------------------------

    def construir_contexto(
        self,
        resultados: List[Dict[str, Any]]
    ) -> str:
        contexto = []
        for chunk in resultados:
            bloque = (
                f"[Fecha: {chunk.get('date', 'N/A')}]\n"
                f"{chunk['text']}"
            )
            contexto.append(bloque)

        return "\n\n---\n\n".join(contexto)


# ============================================================
# PRUEBA DIRECTA
# ============================================================

# if __name__ == "__main__":
#     engine = DiarioQueryEngine()

#     pregunta = input("\n📝 Escribe tu pregunta: ")

#     resultados = engine.buscar(pregunta, k=5)
#     contexto = engine.construir_contexto(resultados)

#     print("\n📚 CONTEXTO RECUPERADO:\n")
#     print(contexto)
