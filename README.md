# Enterprise Agentic RAG Assistant

## Secure Enterprise Knowledge Retrieval with AI Agents

An AI-powered enterprise knowledge assistant built using Python, LangGraph, LangChain, Ollama, Qdrant, FastAPI, Streamlit, and Docker.

## Key Features

- Agentic Retrieval-Augmented Generation (RAG)
- Local LLM using Llama 3.2 through Ollama
- Vector search using Qdrant
- LangGraph agent orchestration
- JWT authentication
- Role-based access control (Employee, HR, IT, Admin)
- Admin-restricted document uploads
- Verified and withheld answer responses
- FastAPI backend and Streamlit frontend
- Docker Compose deployment

## Security Testing

- 21 automated tests passed using pytest
- HR users can access authorized HR documents
- Employee users are restricted from confidential HR information
- Admin document uploads are protected by authorization checks

## Technology Stack

Python | LangGraph | LangChain | Ollama | Qdrant | FastAPI | Streamlit | Docker | pytest

## Project Status

Core application implemented and tested locally using Docker.

Additional architecture documentation and demonstration materials are in progress.
## System Architecture

View the [System Architecture Diagram](docs/architecture.md) to understand how Streamlit, FastAPI, JWT authentication, LangGraph, Qdrant, and Ollama work together.

## Installation and Setup

### Prerequisites

- Python 3.11
- Docker Desktop
- Ollama with Llama 3.2 and nomic-embed-text models
- Qdrant vector database

### 1. Clone the repository

```bash
git clone https://github.com/Jyothi162/enterprise-agentic-rag.git
cd enterprise-agentic-rag
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and configure the required environment variables, including a secure `JWT_SECRET`.

Never commit `.env` to GitHub.

### 3. Start external services

Ensure Ollama is running with the required models and Qdrant is available on port 6333.

The current Docker Compose configuration connects to these services through `host.docker.internal`.

### 4. Start the application

```bash
docker compose up -d --build
```

### 5. Open the application

Streamlit interface:

http://localhost:8503

FastAPI documentation:

http://localhost:8002/docs

### 6. Generate a development test token

For local testing:

```bash
python -m tools.create_test_token employee
```

Paste the generated JWT into the Streamlit interface.

Test tokens expire after 15 minutes. This token-generation utility is intended for development, not production authentication.

### 7. Run automated tests

```bash
docker compose exec api python -m pytest tests/test_rbac.py tests/test_admin_upload.py -v
```

Latest local result: **21 tests passed**.

## Security Notice

This is a portfolio and research demonstration. The current application uses development JWT tokens and locally configured services. Additional security hardening and evaluation are required before production deployment.