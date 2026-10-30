from fastapi.testclient import TestClient

from app.main import app
from app.services.student_service import student_service


client = TestClient(app)


def valid_student() -> dict[str, object]:
    return {
        "name": "Asha Rao",
        "email": "asha@example.com",
        "age": 21,
        "course": "Computer Science",
    }


def setup_function() -> None:
    student_service.clear()


def test_add_student() -> None:
    response = client.post("/api/students", json=valid_student())

    assert response.status_code == 201
    assert response.json() == {"id": 1, **valid_student()}


def test_add_student_rejects_duplicate_email() -> None:
    client.post("/api/students", json=valid_student())

    response = client.post("/api/students", json=valid_student())

    assert response.status_code == 409
    assert response.json()["detail"] == "A student with this email already exists."


def test_add_student_validates_input() -> None:
    invalid_student = valid_student()
    invalid_student["age"] = 0

    response = client.post("/api/students", json=invalid_student)

    assert response.status_code == 422


def test_view_all_students() -> None:
    client.post("/api/students", json=valid_student())

    response = client.get("/api/students")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, **valid_student()}]


def test_view_all_students_is_empty_initially() -> None:
    response = client.get("/api/students")

    assert response.status_code == 200
    assert response.json() == []


def test_view_student_by_id() -> None:
    client.post("/api/students", json=valid_student())

    response = client.get("/api/students/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, **valid_student()}


def test_view_unknown_student_returns_not_found() -> None:
    response = client.get("/api/students/999")

    assert response.status_code == 404


def test_delete_student() -> None:
    client.post("/api/students", json=valid_student())

    response = client.delete("/api/students/1")

    assert response.status_code == 204
    assert client.get("/api/students/1").status_code == 404


def test_delete_unknown_student_returns_not_found() -> None:
    response = client.delete("/api/students/999")

    assert response.status_code == 404
