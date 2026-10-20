from pathlib import Path

from pypdf import PdfReader

from .config import CHUNK_OVERLAP, CHUNK_SIZE


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
    return "\n\n".join(pages)


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if len(chunk) < size:
            chunks.append(chunk)
            break
        last_break = max(chunk.rfind(". "), chunk.rfind("; "), chunk.rfind(", "))
        if last_break > size // 2:
            chunk = chunk[: last_break + 1]
            end = start + len(chunk)
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]
