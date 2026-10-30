from fastapi.testclient import TestClient

from app.main import app
from app.services.library_service import library_service


client = TestClient(app)


def setup_function() -> None:
    library_service.clear()


def create_book() -> None:
    client.post("/api/books", json={
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "total_copies": 2,
    })


def create_member() -> None:
    client.post("/api/members", json={
        "name": "Asha Rao",
        "email": "asha@example.com",
        "membership_number": "LIB-001",
    })


def test_book_crud() -> None:
    create_response = client.post("/api/books", json={
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "total_copies": 2,
    })
    assert create_response.status_code == 201

    update_response = client.put("/api/books/1", json={
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "total_copies": 3,
    })
    assert update_response.status_code == 200
    assert update_response.json()["available_copies"] == 3

    assert client.delete("/api/books/1").status_code == 204


def test_member_crud() -> None:
    create_response = client.post("/api/members", json={
        "name": "Asha Rao",
        "email": "asha@example.com",
        "membership_number": "LIB-001",
    })
    assert create_response.status_code == 201

    update_response = client.put("/api/members/1", json={
        "name": "Asha R.",
        "email": "asha@example.com",
        "membership_number": "LIB-001",
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Asha R."

    assert client.delete("/api/members/1").status_code == 204


def test_issue_and_return_book() -> None:
    create_book()
    create_member()

    issue_response = client.post("/api/loans", json={
        "book_id": 1,
        "member_id": 1,
        "due_at": "2026-11-15T00:00:00Z",
    })
    assert issue_response.status_code == 201
    assert client.get("/api/books/1").json()["available_copies"] == 1

    assert client.delete("/api/members/1").status_code == 409

    return_response = client.post("/api/loans/1/return")
    assert return_response.status_code == 200
    assert return_response.json()["returned_at"] is not None
    assert client.get("/api/books/1").json()["available_copies"] == 2
