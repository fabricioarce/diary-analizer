"""
Indexador Vectorial de Diario Personal
-------------------------------------
Convierte chunks de texto en embeddings y los indexa en FAISS.

Responsabilidades:
- Cargar chunks procesados
- Generar embeddings semánticos
- Crear índice FAISS
- Guardar índice + metadata textual
"""

import json
import logging
from typing import List, Dict, Any

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from pathlib import Path


# ============================================================
# CONFIGURACIÓN DE LOGGING
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

class DiarioVectorIndexer:
    """
    Genera embeddings y crea una base vectorial FAISS
    a partir de chunks de diario personal.
    """

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small"
    ):
        logger.info(f"Cargando modelo de embeddings: {model_name}")
        self.model = SentenceTransformer(
            model_name,
            device="cpu"
        )
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Modelo cargado | Dimensión: {self.dimension}")

        self.index: faiss.Index | None = None
        self.metadata: List[Dict[str, Any]] = []

    # --------------------------------------------------------

    def cargar_chunks(self, archivo_chunks: Path) -> List[Dict[str, Any]]:
        logger.info(f"Cargando chunks desde: {archivo_chunks}")
        with open(archivo_chunks, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        logger.info(f"{len(chunks)} chunks cargados")
        return chunks

    # --------------------------------------------------------

    def generar_embeddings(self, textos: List[str]) -> np.ndarray:
        logger.info("Generando embeddings...")
        embeddings = self.model.encode(
            textos,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        logger.info("Embeddings generados correctamente")
        return embeddings.astype("float32")

    # --------------------------------------------------------

    def crear_indice(self, embeddings: np.ndarray) -> None:
        logger.info("Creando índice FAISS (IndexFlatIP)")
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)

        logger.info(f"Índice FAISS creado | Vectores: {self.index.ntotal}")

    # --------------------------------------------------------

    def guardar(self, ruta_index: Path, ruta_metadata: Path) -> None:
        if self.index is None:
            raise RuntimeError("No hay índice para guardar")

        logger.info(f"Guardando índice FAISS en: {ruta_index}")
        faiss.write_index(self.index, str(ruta_index))

        logger.info(f"Guardando metadata en: {ruta_metadata}")
        with open(ruta_metadata, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        logger.info("Persistencia completada")

    # --------------------------------------------------------

    def indexar_desde_chunks(
        self,
        archivo_chunks: str,
        ruta_index: str,
        ruta_metadata: str
    ) -> None:
        """
        Pipeline completo:
        chunks → embeddings → FAISS → guardado
        """
        chunks = self.cargar_chunks(archivo_chunks)

        textos = [chunk["text"] for chunk in chunks]
        self.metadata = chunks  # solo texto + info, sin embeddings

        embeddings = self.generar_embeddings(textos)
        self.crear_indice(embeddings)
        self.guardar(ruta_index, ruta_metadata)


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":
    indexer = DiarioVectorIndexer()
    
    from backend.app.config import CHUNKS_FILE, FAISS_INDEX_FILE, METADATA_FILE

    indexer.indexar_desde_chunks(
        CHUNKS_FILE, # == archivo_chunks="data/diario_chunks.json",
        FAISS_INDEX_FILE, # == ruta_index="data/diario_index.faiss",
        METADATA_FILE # == ruta_metadata="data/diario_metadata.json"
    )

    logger.info("✓ Indexación del diario completada con éxito")
