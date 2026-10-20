from google import genai

from .config import EMBEDDING_MODEL, LLM_MODEL, get_api_key

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_api_key())
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    client = get_client()
    result = client.models.embed_content(model=EMBEDDING_MODEL, contents=texts)
    return [e.values for e in result.embeddings]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def generate(prompt: str) -> str:
    client = get_client()
    response = client.models.generate_content(model=LLM_MODEL, contents=prompt)
    return response.text or ""
