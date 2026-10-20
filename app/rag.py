from dataclasses import dataclass

from .gemini import embed_text, generate
from .store import query

SYSTEM_PROMPT = """Eres un asistente de contabilidad que responde consultas sobre facturas y recibos de venta de una empresa.

REGLAS ESTRICTAS:
1. Responde SOLO con la información de los fragmentos de facturas que recibas en el contexto. No inventes datos ni uses conocimiento externo.
2. Cita siempre el número de factura, cliente, fecha y cantidades exactas que aparezcan en el contexto.
3. Si la información no está en el contexto, di claramente: "No encuentro esa información en las facturas indexadas."
4. Si hay varias facturas relevantes, menciona todas.
5. Escribe importes con coma decimal y símbolo EUR (ej: 1.015,50 EUR).
6. Responde en español, de forma breve y directa. Sin rodeos.
"""

CONTEXT_PROMPT = """CONTEXTO - fragmentos de facturas encontrados:

{contexto}

---

PREGUNTA DEL USUARIO: {pregunta}

Responde siguiendo las reglas."""


@dataclass
class Respuesta:
    texto: str
    fuentes: list[dict]


def buscar_contexto(pregunta: str, top_k: int = 5) -> dict:
    vector = embed_text(pregunta)
    return query(vector, top_k=top_k)


def preguntar(pregunta: str, top_k: int = 5) -> Respuesta:
    r = buscar_contexto(pregunta, top_k)

    bloques = []
    fuentes = []
    for doc, meta in zip(r["documents"][0], r["metadatas"][0]):
        bloques.append(f"[Fuente: {meta['source']}, fragmento {meta['chunk'] + 1}]\n{doc}")
        fuentes.append({"source": meta["source"], "chunk": int(meta["chunk"])})

    contexto = "\n\n".join(bloques) if bloques else "(sin resultados)"

    prompt = SYSTEM_PROMPT + "\n\n" + CONTEXT_PROMPT.format(contexto=contexto, pregunta=pregunta)
    texto = generate(prompt)

    return Respuesta(texto=texto.strip(), fuentes=fuentes)
