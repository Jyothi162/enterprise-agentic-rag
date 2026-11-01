
import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document as WordDocument


DOCUMENTS_DIR = Path("data/documents")

ALLOWED_DEPARTMENTS = {"public", "hr", "it"}


def extract_department(text: str) -> str:
    match = re.search(
        r"(?im)^Department:\s*(public|hr|it)\s*$",
        text,
    )

    if not match:
        raise ValueError(
            "Document is missing a valid Department header. "
            "Allowed departments: public, hr, it."
        )

    return match.group(1).lower()


def load_documents(folder=DOCUMENTS_DIR):
    documents = []

    for file_path in sorted(Path(folder).rglob("*")):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            text = file_path.read_text(encoding="utf-8")

            if not text.strip():
                continue

            department = extract_department(text)

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(file_path),
                        "department": department,
                    },
                )
            )

        elif suffix == ".pdf":
            reader = PdfReader(str(file_path))

            pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]

            full_text = "\n".join(pages)
            department = extract_department(full_text)

            for page_number, text in enumerate(pages, start=1):
                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": str(file_path),
                                "page": page_number,
                                "department": department,
                            },
                        )
                    )

        elif suffix == ".docx":
            word_doc = WordDocument(str(file_path))

            text = "\n".join(
                paragraph.text
                for paragraph in word_doc.paragraphs
                if paragraph.text.strip()
            )

            if text.strip():
                department = extract_department(text)

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": str(file_path),
                            "department": department,
                        },
                    )
                )

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
    )

    return splitter.split_documents(documents)


if __name__ == "__main__":
    documents = load_documents()
    chunks = split_documents(documents)

    print(f"Loaded documents: {len(documents)}")
    print(f"Created chunks: {len(chunks)}")

    for chunk in chunks:
        print("\nSource:", chunk.metadata)
        print("Text:", chunk.page_content[:200])
