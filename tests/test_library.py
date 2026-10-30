from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.library_service import library_service
from app.services.student_service import student_service


client = TestClient(app)


def setup_function() -> None:
    student_service.clear()
    library_service.clear()


def create_student() -> int:
    response = client.post(
        "/api/students",
        json={
            "name": "Asha Rao",
            "email": "asha@example.com",
            "age": 21,
            "course": "Computer Science",
        },
    )
    return response.json()["id"]


def create_book(copies: int = 1) -> int:
    response = client.post(
        "/api/library/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "copies": copies,
        },
    )
    return response.json()["id"]


def test_add_book() -> None:
    response = client.post(
        "/api/library/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "copies": 2,
        },
    )

    assert response.status_code == 201
    assert response.json()["available_copies"] == 2
    assert response.json()["total_copies"] == 2


def test_borrow_and_return_book() -> None:
    student_id = create_student()
    book_id = create_book()
    borrowed = client.post(
        "/api/library/loans",
        json={"student_id": student_id, "book_id": book_id, "loan_days": 14},
    )

    assert borrowed.status_code == 201
    assert borrowed.json()["returned_at"] is None
    assert client.get("/api/library/books").json()[0]["available_copies"] == 0

    returned = client.post(f"/api/library/loans/{borrowed.json()['id']}/return")

    assert returned.status_code == 200
    assert returned.json()["returned_at"] is not None
    assert client.get("/api/library/books").json()[0]["available_copies"] == 1


def test_borrow_rejects_duplicate_active_loan() -> None:
    student_id = create_student()
    book_id = create_book()
    client.post("/api/library/loans", json={"student_id": student_id, "book_id": book_id})

    response = client.post(
        "/api/library/loans",
        json={"student_id": student_id, "book_id": book_id},
    )

    assert response.status_code == 409


def test_student_borrowing_history() -> None:
    student_id = create_student()
    book_id = create_book()
    client.post("/api/library/loans", json={"student_id": student_id, "book_id": book_id})

    response = client.get(f"/api/library/students/{student_id}/loans")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["student_id"] == student_id


def test_overdue_loan_calculates_fine() -> None:
    student_id = create_student()
    book_id = create_book()
    loan = client.post(
        "/api/library/loans",
        json={"student_id": student_id, "book_id": book_id},
    ).json()
    library_service._loans[loan["id"]].due_at = datetime.now(UTC) - timedelta(days=3)

    response = client.get("/api/library/loans/overdue")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["fine"] == 3.0


def test_reservation_and_cancellation() -> None:
    student_id = create_student()
    book_id = create_book()
    created = client.post(
        "/api/library/reservations",
        json={"student_id": student_id, "book_id": book_id},
    )

    assert created.status_code == 201
    assert created.json()["status"] == "active"

    cancelled = client.delete(f"/api/library/reservations/{created.json()['id']}")

    assert cancelled.status_code == 204
    reservations = client.get("/api/library/reservations").json()
    assert reservations[0]["status"] == "cancelled"