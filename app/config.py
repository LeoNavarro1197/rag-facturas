import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-3.8-flash"

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
