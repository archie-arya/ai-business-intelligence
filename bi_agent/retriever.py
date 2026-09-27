import os

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from langchain_ollama import OllamaEmbeddings


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/retail_bi",
)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    ),
)


def retrieve(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Find the most semantically relevant document chunks
    for a natural-language query.
    """

    # Convert the user's question into the same vector
    # representation used during document ingestion.
    query_embedding = Vector(embeddings.embed_query(query))

    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    source,
                    chunk_index,
                    content,
                    metadata,
                    1 - (embedding <=> %s) AS similarity
                FROM public.rag_documents
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (
                    query_embedding,
                    query_embedding,
                    top_k,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "source": row[1],
            "chunk_index": row[2],
            "content": row[3],
            "metadata": row[4],
            "similarity": float(row[5]),
        }
        for row in rows
    ]


if __name__ == "__main__":
    query = input("Query: ")

    results = retrieve(query)

    for result in results:
        print("\n" + "=" * 80)
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk_index']}")
        print(f"Similarity: {result['similarity']:.4f}")
        print("-" * 80)
        print(result["content"])