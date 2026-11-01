
import io
from pathlib import Path
from uuid import uuid4

from docx import Document as WordDocument
from langchain_core.documents import Document
from pypdf import PdfReader

from rag.ingest import split_documents
from rag.retriever import get_vector_store


ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
ALLOWED_DEPARTMENTS = {"public", "hr", "it"}


def extract_uploaded_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        text = content.decode("utf-8")

    elif extension == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif extension == ".docx":
        document = WordDocument(io.BytesIO(content))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        raise ValueError("Unsupported file type")

    if not text.strip():
        raise ValueError(
            "The uploaded document contains no extractable text."
        )

    return text


def ingest_uploaded_document(
    filename: str,
    content: bytes,
    department: str,
    uploaded_by: str,
):
    department = department.lower().strip()

    if department not in ALLOWED_DEPARTMENTS:
        raise ValueError("Invalid department")

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type")

    text = extract_uploaded_text(filename, content)

    document_id = str(uuid4())

    document = Document(
        page_content=text,
        metadata={
            "source": f"upload:{document_id}",
            "filename": Path(filename).name,
            "department": department,
            "uploaded_by": uploaded_by,
            "document_id": document_id,
        },
    )

    chunks = split_documents([document])

    if not chunks:
        raise ValueError("No document chunks were created")

    vector_store = get_vector_store()

    point_ids = [str(uuid4()) for _ in chunks]

    vector_store.add_documents(
        documents=chunks,
        ids=point_ids,
    )

    return {
        "document_id": document_id,
        "filename": Path(filename).name,
        "department": department,
        "chunks_created": len(chunks),
        "uploaded_by": uploaded_by,
        "status": "STORED_IN_QDRANT",
    }
