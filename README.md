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
