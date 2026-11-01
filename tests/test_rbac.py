
import pytest

from rag.retriever import retrieve_documents
from tools.access_control import get_allowed_departments


@pytest.mark.parametrize(
    "role, expected_departments",
    [
        ("employee", {"public"}),
        ("hr", {"public", "hr"}),
        ("it", {"public", "it"}),
        ("admin", {"public", "hr", "it"}),
    ],
)
def test_role_based_retrieval(role, expected_departments):
    documents = retrieve_documents(
        query="What does the HR salary policy say?",
        role=role,
        k=10,
    )

    assert documents, f"No documents returned for {role}"

    for document in documents:
        department = document.metadata.get("department")

        assert department in expected_departments, (
            f"Unauthorized document retrieved for {role}: "
            f"{document.metadata}"
        )


def test_employee_cannot_access_hr_documents():
    documents = retrieve_documents(
        query="HR salary policy confidential employee salary records",
        role="employee",
        k=10,
    )

    sources = [
        doc.metadata.get("source", "")
        for doc in documents
    ]

    assert not any(
        "hr_salary_policy.txt" in source
        for source in sources
    )


def test_hr_can_access_salary_policy():
    documents = retrieve_documents(
        query="HR salary policy confidential salary adjustment",
        role="hr",
        k=10,
    )

    sources = [
        doc.metadata.get("source", "")
        for doc in documents
    ]

    assert any(
        "hr_salary_policy.txt" in source
        for source in sources
    )


def test_unknown_role_is_rejected():
    with pytest.raises(ValueError):
        get_allowed_departments("guest")

def test_it_cannot_access_hr_documents():
    documents = retrieve_documents(
        query="Confidential HR salary records",
        role="it",
        k=10,
    )

    for doc in documents:
        assert doc.metadata.get("department") != "hr"


def test_employee_cannot_access_it_admin_documents():
    documents = retrieve_documents(
        query="Privileged account changes and system access logs",
        role="employee",
        k=10,
    )

    for doc in documents:
        assert doc.metadata.get("department") != "it"
