import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import PDF_DIR
from app.pipeline import indexar_pdf
from app.store import count, reset as reset_index


def main():
    if "--reset" in sys.argv:
        print("Borrando índice anterior...")
        reset_index()

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {PDF_DIR}")
        print("Copia tus facturas a esa carpeta y vuelve a ejecutar.")
        return

    print(f"Indexando {len(pdfs)} PDFs de {PDF_DIR}...")
    total = 0
    for pdf_path in pdfs:
        trozos = indexar_pdf(pdf_path)
        if trozos == 0:
            print(f"  {pdf_path.name}: sin texto extraible o vacío - omitido")
        else:
            print(f"  {pdf_path.name}: {trozos} trozos indexados")
            total += trozos

    print(f"\nListo: {total} trozos en total. Índice con {count()} documentos.")


if __name__ == "__main__":
    main()
