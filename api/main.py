from rag.upload_service import ingest_uploaded_document
from pathlib import Path
from fastapi import UploadFile, File, Form
from fastapi import Depends
from tools.auth import require_admin
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from agents.graph import graph
from tools.access_control import get_allowed_departments
from tools.auth import get_current_user, require_admin

app = FastAPI(
    title="Enterprise Agentic RAG Assistant",
    description="Role-aware enterprise knowledge assistant using LangGraph, Qdrant and Ollama.",
    version="1.0.0",
)



class AskRequest(BaseModel):
    question: str = Field(min_length=1)

    model_config = {"extra": "forbid"}



class AskResponse(BaseModel):
    question: str
    role: str
    answer: str
    verification: str
    final_status: str
    revision_count: int
    sources: list


@app.get("/")
def home():
    return {
        "message": "Enterprise Agentic RAG API is running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/ask", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    user=Depends(get_current_user),
):
    # Role comes from the verified JWT
    role = user["role"]

    try:
        result = graph.invoke({
            "question": request.question,
            "role": role,
            "context": "",
            "answer": "",
            "sources": [],
            "verification": "",
            "revision_count": 0,
            "final_status": "",
        })

        return AskResponse(
            question=result["question"],
            role=role,
            answer=result["answer"],
            verification=result["verification"],
            final_status=result["final_status"],
            revision_count=result["revision_count"],
            sources=(
                result["sources"]
                if result["final_status"] == "VERIFIED"
                else []
            ),
        )

    except Exception as exc:
        print(f"Question processing failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process question",
        ) from exc


@app.get("/admin/check")
def check_admin_access(user=Depends(require_admin)):
    return {
        "message": "Administrator access granted",
        "username": user["username"],
        "role": user["role"],
    }

@app.get("/admin/check")
def check_admin_access(user=Depends(require_admin)):
    return {
        "message": "Administrator access granted",
        "username": user["username"],
        "role": user["role"],
    }

@app.get("/auth/me")
def get_my_identity(user=Depends(get_current_user)):
    return {
        "username": user["username"],
        "role": user["role"],
    }


ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
ALLOWED_DEPARTMENTS = {"public", "hr", "it"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@app.post("/admin/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    user=Depends(require_admin),
):
    department = department.lower().strip()

    if department not in ALLOWED_DEPARTMENTS:
        raise HTTPException(
            status_code=400,
            detail="Invalid department. Choose public, hr, or it.",
        )

    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only TXT, PDF, and DOCX files are supported.",
        )

    content = await file.read(MAX_UPLOAD_BYTES + 1)

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 5 MB upload limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Cannot upload an empty file.",
        )

    
    try:
        result = ingest_uploaded_document(
            filename=filename,
            content=content,
            department=department,
            uploaded_by=user["username"],
        )

        return result

    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
