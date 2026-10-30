from datetime import UTC, datetime, timedelta
from threading import Lock

from app.models.library import Book, Loan, Reservation
from app.services.student_service import student_service


DAILY_FINE = 1.0


class LibraryError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


class LibraryService:
    def __init__(self) -> None:
        self._books: dict[int, Book] = {}
        self._loans: dict[int, Loan] = {}
        self._reservations: dict[int, Reservation] = {}
        self._total_copies: dict[int, int] = {}
        self._next_book_id = 1
        self._next_loan_id = 1
        self._next_reservation_id = 1
        self._lock = Lock()

    def create_book(self, data: dict[str, object]) -> Book:
        with self._lock:
            isbn = str(data["isbn"]).lower()
            if any(book.isbn.lower() == isbn for book in self._books.values()):
                raise LibraryError(409, "A book with this ISBN already exists.")
            copies = int(data["copies"])
            book = Book(
                id=self._next_book_id,
                title=str(data["title"]),
                author=str(data["author"]),
                isbn=str(data["isbn"]),
                available_copies=copies,
            )
            self._books[book.id] = book
            self._total_copies[book.id] = copies
            self._next_book_id += 1
            return book

    def get_books(self) -> list[Book]:
        with self._lock:
            return list(self._books.values())

    def borrow(self, student_id: int, book_id: int, loan_days: int) -> Loan:
        with self._lock:
            if student_service.get_by_id(student_id) is None:
                raise LibraryError(404, f"Student with ID {student_id} was not found.")
            book = self._books.get(book_id)
            if book is None:
                raise LibraryError(404, f"Book with ID {book_id} was not found.")
            if book.available_copies < 1:
                raise LibraryError(409, "No copies of this book are available.")
            if any(
                loan.student_id == student_id
                and loan.book_id == book_id
                and loan.returned_at is None
                for loan in self._loans.values()
            ):
                raise LibraryError(409, "This student already has an active loan for this book.")

            now = datetime.now(UTC)
            loan = Loan(
                id=self._next_loan_id,
                student_id=student_id,
                book_id=book_id,
                borrowed_at=now,
                due_at=now + timedelta(days=loan_days),
            )
            self._loans[loan.id] = loan
            self._next_loan_id += 1
            book.available_copies -= 1
            return loan

    def return_book(self, loan_id: int) -> Loan:
        with self._lock:
            loan = self._loans.get(loan_id)
            if loan is None:
                raise LibraryError(404, f"Loan with ID {loan_id} was not found.")
            if loan.returned_at is not None:
                raise LibraryError(409, "This loan has already been returned.")
            loan.returned_at = datetime.now(UTC)
            self._books[loan.book_id].available_copies += 1
            self._fulfill_next_reservation(loan.book_id)
            return loan

    def get_loans(self) -> list[Loan]:
        with self._lock:
            return list(self._loans.values())

    def get_student_loans(self, student_id: int) -> list[Loan]:
        with self._lock:
            if student_service.get_by_id(student_id) is None:
                raise LibraryError(404, f"Student with ID {student_id} was not found.")
            return [loan for loan in self._loans.values() if loan.student_id == student_id]

    def calculate_fine(self, loan: Loan, now: datetime | None = None) -> float:
        end = loan.returned_at or (now or datetime.now(UTC))
        if end <= loan.due_at:
            return 0.0
        overdue_days = max(1, (end - loan.due_at).days)
        return round(overdue_days * DAILY_FINE, 2)

    def reserve(self, student_id: int, book_id: int) -> Reservation:
        with self._lock:
            if student_service.get_by_id(student_id) is None:
                raise LibraryError(404, f"Student with ID {student_id} was not found.")
            if book_id not in self._books:
                raise LibraryError(404, f"Book with ID {book_id} was not found.")
            if any(
                reservation.student_id == student_id
                and reservation.book_id == book_id
                and reservation.status == "active"
                for reservation in self._reservations.values()
            ):
                raise LibraryError(409, "This student already has an active reservation for this book.")
            reservation = Reservation(
                id=self._next_reservation_id,
                student_id=student_id,
                book_id=book_id,
                created_at=datetime.now(UTC),
            )
            self._reservations[reservation.id] = reservation
            self._next_reservation_id += 1
            return reservation

    def cancel_reservation(self, reservation_id: int) -> bool:
        with self._lock:
            reservation = self._reservations.get(reservation_id)
            if reservation is None:
                return False
            if reservation.status != "active":
                raise LibraryError(409, "This reservation is not active.")
            reservation.status = "cancelled"
            return True

    def get_reservations(self, student_id: int | None = None) -> list[Reservation]:
        with self._lock:
            reservations = list(self._reservations.values())
            if student_id is not None:
                reservations = [item for item in reservations if item.student_id == student_id]
            return reservations

    def _fulfill_next_reservation(self, book_id: int) -> None:
        queued = sorted(
            (
                item for item in self._reservations.values()
                if item.book_id == book_id and item.status == "active"
            ),
            key=lambda item: item.created_at,
        )
        if queued:
            queued[0].status = "available"

    def total_copies(self, book_id: int) -> int:
        with self._lock:
            return self._total_copies.get(book_id, 0)

    def clear(self) -> None:
        with self._lock:
            self._books.clear()
            self._loans.clear()
            self._reservations.clear()
            self._total_copies.clear()
            self._next_book_id = 1
            self._next_loan_id = 1
            self._next_reservation_id = 1


library_service = LibraryService()