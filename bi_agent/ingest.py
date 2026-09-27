import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb
from pgvector.psycopg import register_vector
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


DOCUMENT_DIR = Path("data/rag")

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

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
)


def load_documents():
    documents = []

    for path in DOCUMENT_DIR.glob("*.md"):
        documents.append({
            "source": path.name,
            "content": path.read_text(encoding="utf-8"),
        })

    return documents


def ingest():
    documents = load_documents()

    print(f"Found {len(documents)} documents.")

    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)

        with conn.cursor() as cursor:

            for document in documents:

                chunks = splitter.split_text(
                    document["content"]
                )

                print(
                    f"{document['source']}: "
                    f"{len(chunks)} chunks"
                )

                for chunk_index, chunk in enumerate(chunks):

                    embedding = embeddings.embed_query(chunk)

                    cursor.execute(
                        """
                        INSERT INTO rag_documents
                            (
                                source,
                                chunk_index,
                                content,
                                metadata,
                                embedding
                            )
                        VALUES
                            (%s, %s, %s, %s, %s)
                        ON CONFLICT (source, chunk_index)
                        DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                        """,
                        (
                            document["source"],
                            chunk_index,
                            chunk,
                            Jsonb({}),
                            embedding,
                        ),
                    )

        conn.commit()

    print("Ingestion complete.")


if __name__ == "__main__":
    ingest()