"""Capa de almacenamiento vectorial.

Usa PostgreSQL + pgvector si DATABASE_URL esta definida (produccion).
Si no, usa ChromaDB local (desarrollo).

Ambos backends exponen la misma interfaz: add_documents, query, count, reset.
"""

from .config import DATABASE_URL, EMBEDDING_DIM, INDEX_DIR

COLLECTION_NAME = "facturas"


# ---------------------------------------------------------------- PostgreSQL
class PgVectorStore:
    def __init__(self, dsn: str):
        from psycopg_pool import ConnectionPool
        from pgvector.psycopg import register_vector

        self.pool = ConnectionPool(dsn, min_size=1, max_size=5, open=True)
        self._init_schema()

    def _init_schema(self):
        with self.pool.connection() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {COLLECTION_NAME} (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    chunk INTEGER NOT NULL,
                    total_chunks INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector({EMBEDDING_DIM}) NOT NULL
                )
                """
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {COLLECTION_NAME}_source_idx "
                f"ON {COLLECTION_NAME} (source)"
            )

    def add_documents(self, ids, embeddings, documents, metadatas):
        from pgvector import Vector

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                for id_, emb, doc, meta in zip(ids, embeddings, documents, metadatas):
                    cur.execute(
                        f"""
                        INSERT INTO {COLLECTION_NAME}
                            (id, source, chunk, total_chunks, content, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            total_chunks = EXCLUDED.total_chunks
                        """,
                        (
                            id_,
                            meta["source"],
                            int(meta["chunk"]),
                            int(meta["total_chunks"]),
                            doc,
                            Vector(emb),
                        ),
                    )

    def query(self, embedding, top_k=5):
        from pgvector import Vector

        with self.pool.connection() as conn:
            rows = conn.execute(
                f"""
                SELECT source, chunk, content, embedding <=> %s AS dist
                FROM {COLLECTION_NAME}
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (Vector(embedding), Vector(embedding), top_k),
            ).fetchall()
        return {
            "documents": [[r[2] for r in rows]],
            "metadatas": [[{"source": r[0], "chunk": r[1]} for r in rows]],
            "distances": [[float(r[3]) for r in rows]],
        }

    def count(self) -> int:
        with self.pool.connection() as conn:
            return conn.execute(f"SELECT COUNT(*) FROM {COLLECTION_NAME}").fetchone()[0]

    def reset(self):
        with self.pool.connection() as conn:
            conn.execute(f"TRUNCATE {COLLECTION_NAME}")


# -------------------------------------------------------------------- Chroma
class ChromaStore:
    def __init__(self):
        import chromadb

        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(INDEX_DIR))
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def add_documents(self, ids, embeddings, documents, metadatas):
        self.collection.upsert(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def query(self, embedding, top_k=5):
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)


# -------------------------------------------------------------------- Fabrica
_store = None


def _build_store():
    if DATABASE_URL:
        return PgVectorStore(DATABASE_URL)
    return ChromaStore()


def get_store():
    global _store
    if _store is None:
        _store = _build_store()
    return _store


def add_documents(ids, embeddings, documents, metadatas):
    get_store().add_documents(ids, embeddings, documents, metadatas)


def query(embedding, top_k=5):
    return get_store().query(embedding, top_k)


def count() -> int:
    return get_store().count()


def reset():
    get_store().reset()
