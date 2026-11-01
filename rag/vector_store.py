
import os

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from rag.ingest import load_documents, split_documents


load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "enterprise_knowledge_rbac"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"


def get_embeddings():
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_URL
    )


def ingest_into_qdrant():
    documents = load_documents()
    chunks = split_documents(documents)

    if not chunks:
        print("No document chunks found.")
        return

    client = QdrantClient(url=QDRANT_URL)

    if client.collection_exists(COLLECTION_NAME):
        print("Collection already exists. Skipping ingestion.")
        return

    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME
    )

    print(f"Successfully stored {len(chunks)} chunks in Qdrant!")

    collection = client.get_collection(COLLECTION_NAME)
    print(f"Stored vectors: {collection.points_count}")


if __name__ == "__main__":
    ingest_into_qdrant()
