
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Filter, FieldCondition, MatchAny

from rag.vector_store import (
    get_embeddings,
    QDRANT_URL,
    COLLECTION_NAME,
)
from tools.access_control import get_allowed_departments


def get_vector_store():
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        url=QDRANT_URL,
    )


def retrieve_documents(query, role="employee", k=3):
    # Determine which departments the user can access
    allowed_departments = get_allowed_departments(role)

    # Apply the filter inside Qdrant before retrieving text
    access_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.department",
                match=MatchAny(any=allowed_departments),
            )
        ]
    )

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query=query,
        k=k,
        filter=access_filter,
    )

    return documents


if __name__ == "__main__":
    question = "What does the HR salary policy say?"

    for role in ["employee", "hr", "it", "admin"]:
        print(f"\n--- Role: {role.upper()} ---")

        results = retrieve_documents(
            query=question,
            role=role,
            k=3,
        )

        for doc in results:
            print("Source:", doc.metadata.get("source"))
            print("Department:", doc.metadata.get("department"))
            print("Content:", doc.page_content[:200])

        if not results:
            print("No accessible documents found.")
