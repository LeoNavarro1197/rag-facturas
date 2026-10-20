import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Si DATABASE_URL esta definida, se usa PostgreSQL + pgvector.
# Si no, se usa ChromaDB local (desarrollo).
DATABASE_URL = os.getenv("DATABASE_URL")

EMBEDDING_MODEL = "gemini-embedding-001"
# Dimension fija para pgvector (gemini-embedding-001 soporta 3072, 1536 y 768).
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "pdfs"
INDEX_DIR = BASE_DIR / "data" / "index"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
BATCH_SIZE = 100


def get_api_key() -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")
    return GEMINI_API_KEY
