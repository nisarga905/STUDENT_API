from threading import Lock

from app.models.student import Student


class StudentService:
    """Manage student records in memory.

    A database can replace this service without changing the API routes.
    """

    def __init__(self) -> None:
        self._students: dict[int, Student] = {}
        self._next_id = 1
        self._lock = Lock()

    def create(self, data: dict[str, object]) -> Student:
        with self._lock:
            student = Student(id=self._next_id, **data)
            self._students[student.id] = student
            self._next_id += 1
            return student

    def get_all(self) -> list[Student]:
        with self._lock:
            return list(self._students.values())

    def get_by_id(self, student_id: int) -> Student | None:
        with self._lock:
            return self._students.get(student_id)

    def email_exists(self, email: str) -> bool:
        with self._lock:
            return any(student.email.lower() == email.lower() for student in self._students.values())

    def delete(self, student_id: int) -> bool:
        with self._lock:
            return self._students.pop(student_id, None) is not None

    def clear(self) -> None:
        """Reset all records; primarily used by automated tests."""
        with self._lock:
            self._students.clear()
            self._next_id = 1


student_service = StudentService()
