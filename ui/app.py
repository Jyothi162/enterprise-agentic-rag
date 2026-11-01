
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Enterprise Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🤖 Enterprise Agentic RAG Assistant")

st.caption(
    "Secure Enterprise Knowledge Assistant | "
    "LangGraph • Qdrant • Ollama • FastAPI"
)

# --------------------------------------------------
# Sidebar - Authentication
# --------------------------------------------------

st.sidebar.header("🔐 Authentication")

token = st.sidebar.text_input(
    "JWT Access Token",
    type="password",
    help="Paste your short-lived development JWT token.",
)

st.sidebar.info(
    "Local development mode. "
    "Your role is determined by the authenticated "
    "JWT, not by a role selector."
)

# --------------------------------------------------
# Session state
# --------------------------------------------------

if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

if "active_token" not in st.session_state:
    st.session_state.active_token = None

if "active_identity" not in st.session_state:
    st.session_state.active_identity = None

# Clear the displayed identity when the token changes.
if token != st.session_state.active_token:
    st.session_state.active_token = token
    st.session_state.active_identity = None

# --------------------------------------------------
# Authentication check
# --------------------------------------------------

if not token.strip():
    st.warning(
        "Please enter a JWT access token in the sidebar."
    )
    st.stop()

try:
    auth_response = requests.get(
        f"{API_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=15,
    )

    auth_response.raise_for_status()
    identity = auth_response.json()

except requests.HTTPError as exc:
    if (
        exc.response is not None
        and exc.response.status_code == 401
    ):
        st.error(
            "Invalid or expired JWT token. "
            "Please generate a new token."
        )
    else:
        st.error("Authentication check failed.")

    st.stop()

except requests.RequestException:
    st.error(
        "Cannot connect to FastAPI. "
        "Make sure the backend is running on port 8000."
    )
    st.stop()

username = identity["username"]
role = identity["role"]

st.session_state.active_identity = username

st.sidebar.success(f"Authenticated as: {username}")
st.sidebar.write(f"**Role:** {role.upper()}")

# --------------------------------------------------
# Chat history
# --------------------------------------------------

if username not in st.session_state.chat_histories:
    st.session_state.chat_histories[username] = []

messages = st.session_state.chat_histories[username]

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_histories[username] = []
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("### System Components")
st.sidebar.write("✅ LangGraph Agents")
st.sidebar.write("✅ Qdrant Vector Database")
st.sidebar.write("✅ Ollama LLM")
st.sidebar.write("✅ Role-Based Retrieval")
st.sidebar.write("✅ Answer Verification")

# --------------------------------------------------
# Display previous messages
# --------------------------------------------------

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            st.caption(
                f"Verification status: "
                f"{message.get('status', 'unknown')}"
            )

            for source in message.get("sources", []):
                st.caption(
                    f"{source['citation']} "
                    f"{source['source']}"
                )

# --------------------------------------------------
# Chat input
# --------------------------------------------------

question = st.chat_input(
    "Ask a question about enterprise documents..."
)

if question:
    messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(
            "Retrieving documents and verifying answer..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question,
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=180,
                )

                response.raise_for_status()
                result = response.json()

                answer = result["answer"]
                status = result["final_status"]

                sources = (
                    result.get("sources", [])
                    if status == "VERIFIED"
                    else []
                )

                st.markdown(answer)
                st.caption(
                    f"Verification status: {status}"
                )

                if sources:
                    with st.expander("📚 Retrieved Sources"):
                        for source in sources:
                            st.write(
                                f"{source['citation']} "
                                f"{source['source']}"
                            )

                messages.append({
                    "role": "assistant",
                    "content": answer,
                    "status": status,
                    "sources": sources,
                })

            except requests.HTTPError as exc:
                if (
                    exc.response is not None
                    and exc.response.status_code == 401
                ):
                    st.error(
                        "Your token has expired or is invalid."
                    )

                elif (
                    exc.response is not None
                    and exc.response.status_code == 403
                ):
                    st.error(
                        "Access denied."
                    )

                else:
                    st.error(
                        "The AI backend returned an error."
                    )

            except requests.RequestException:
                st.error(
                    "Cannot connect to the FastAPI backend."
                )

# ---------------------------------------
# ADMIN DOCUMENT UPLOAD
# ---------------------------------------

if role == "admin":
    st.divider()
    st.subheader("📁 Admin Document Upload")

    st.info(
        "Upload enterprise documents to the "
        "Qdrant knowledge base."
    )

    upload_department = st.selectbox(
        "Select document department",
        ["public", "hr", "it"],
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["txt", "pdf", "docx"],
    )

    if st.button("Upload to Knowledge Base"):
        if uploaded_file is None:
            st.warning("Please select a document first.")

        else:
            with st.spinner("Uploading and indexing document..."):
                try:
                    response = requests.post(
                        f"{API_URL}/admin/upload",
                        headers={
                            "Authorization": f"Bearer {token}"
                        },
                        data={
                            "department": upload_department
                        },
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        },
                        timeout=180,
                    )

                    if response.status_code == 200:
                        result = response.json()

                        st.success(
                            "Document uploaded successfully!"
                        )

                        st.write(
                            "Filename:",
                            result["filename"],
                        )

                        st.write(
                            "Department:",
                            result["department"],
                        )

                        st.write(
                            "Chunks created:",
                            result["chunks_created"],
                        )

                    else:
                        st.error(
                            f"Upload failed: {response.text}"
                        )

                except requests.RequestException as exc:
                    st.error(f"Connection error: {exc}")
