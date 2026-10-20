import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.gemini import embed_text
from app.store import count, query


def main():
    print("Documentos en el indice:", count())
    pregunta = sys.argv[1] if len(sys.argv) > 1 else "¿Cuánto costó el aceite de oliva para Restaurante El Olivo?"
    print("Pregunta:", pregunta)
    vector = embed_text(pregunta)
    r = query(vector, top_k=3)
    for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
        print(f"  [dist {dist:.3f}] {meta['source']}: {doc[:100]}...")


if __name__ == "__main__":
    main()
