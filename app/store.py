import chromadb

from .config import INDEX_DIR

COLLECTION_NAME = "facturas"


def get_collection():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME)


def add_documents(ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict]):
    collection = get_collection()
    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query(embedding: list[float], top_k: int = 5) -> dict:
    collection = get_collection()
    return collection.query(query_embeddings=[embedding], n_results=top_k)


def count() -> int:
    return get_collection().count()


def reset():
    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    client.delete_collection(COLLECTION_NAME)
