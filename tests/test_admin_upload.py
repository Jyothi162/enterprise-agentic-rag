
import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.main import app


load_dotenv()

client = TestClient(app)


def create_test_token(role):
    secret = os.getenv("JWT_SECRET")

    if not secret:
        raise RuntimeError("JWT_SECRET is missing")

    payload = {
        "sub": f"demo_{role}",
        "role": role,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=15),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )


@pytest.mark.parametrize(
    "role",
    ["employee", "hr", "it"],
)
def test_non_admin_cannot_upload(role):
    token = create_test_token(role)

    response = client.post(
        "/admin/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        data={"department": "public"},
        files={
            "file": (
                "test.txt",
                b"This is a test document.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 403


def test_upload_without_token():
    response = client.post(
        "/admin/upload",
        data={"department": "public"},
        files={
            "file": (
                "test.txt",
                b"This is a test document.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 401

@pytest.mark.parametrize(
    "department",
    ["finance", "unknown", "secret"],
)
def test_admin_invalid_department(department):
    token = create_test_token("admin")

    response = client.post(
        "/admin/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        data={"department": department},
        files={
            "file": (
                "test.txt",
                b"Test document",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "filename",
    ["malware.exe", "script.py", "archive.zip"],
)
def test_admin_invalid_file_extension(filename):
    token = create_test_token("admin")

    response = client.post(
        "/admin/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        data={"department": "public"},
        files={
            "file": (
                filename,
                b"Test document",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400


def test_admin_empty_file():
    token = create_test_token("admin")

    response = client.post(
        "/admin/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        data={"department": "public"},
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_admin_file_too_large():
    token = create_test_token("admin")

    large_content = b"A" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/admin/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        data={"department": "public"},
        files={
            "file": (
                "large.txt",
                large_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
