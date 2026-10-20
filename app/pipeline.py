from pathlib import Path

from .config import BATCH_SIZE
from .gemini import embed_texts
from .ingest import chunk_text, extract_text
from .store import add_documents


def indexar_pdf(pdf_path: Path) -> int:
    text = extract_text(pdf_path)
    if not text.strip():
        return 0
    chunks = chunk_text(text)
    if not chunks:
        return 0

    ids, embeddings, documents, metadatas = [], [], [], []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        vectors = embed_texts(batch)
        for j, (chunk, vector) in enumerate(zip(batch, vectors)):
            idx = i + j
            ids.append(f"{pdf_path.name}::{idx}")
            embeddings.append(vector)
            documents.append(chunk)
            metadatas.append(
                {
                    "source": pdf_path.name,
                    "chunk": idx,
                    "total_chunks": len(chunks),
                }
            )
    add_documents(ids, embeddings, documents, metadatas)
    return len(chunks)
