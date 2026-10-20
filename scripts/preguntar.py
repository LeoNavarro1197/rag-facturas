import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag import preguntar


def main():
    if len(sys.argv) < 2:
        print('Uso: python scripts/preguntar.py "tu pregunta aquí"')
        print('Ejemplo: python scripts/preguntar.py "¿Cuánto me facturó Panadería La Espiga?"')
        return

    pregunta = " ".join(sys.argv[1:])
    print(f"Pregunta: {pregunta}\n")

    respuesta = preguntar(pregunta)

    print("RESPUESTA:")
    print(respuesta.texto)

    fuentes_unicas = sorted({f["source"] for f in respuesta.fuentes})
    print(f"\nFuentes consultadas: {', '.join(fuentes_unicas)}")


if __name__ == "__main__":
    main()
