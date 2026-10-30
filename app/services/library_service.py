from datetime import datetime
from threading import Lock

from app.models.book import Book
from app.models.loan import Loan
from app.models.member import Member


class LibraryService:
    def __init__(self) -> None:
        self._books: dict[int, Book] = {}
        self._members: dict[int, Member] = {}
        self._loans: dict[int, Loan] = {}
        self._next_book_id = 1
        self._next_member_id = 1
        self._next_loan_id = 1
        self._lock = Lock()

    def create_book(self, data: dict[str, object]) -> Book:
        with self._lock:
            total_copies = int(data["total_copies"])
            book = Book(id=self._next_book_id, **data, available_copies=total_copies)
            self._books[book.id] = book
            self._next_book_id += 1
            return book

    def get_books(self) -> list[Book]:
        with self._lock:
            return list(self._books.values())

    def get_book(self, book_id: int) -> Book | None:
        with self._lock:
            return self._books.get(book_id)

    def update_book(self, book_id: int, data: dict[str, object]) -> Book | None:
        with self._lock:
            book = self._books.get(book_id)
            if book is None:
                return None
            issued = book.total_copies - book.available_copies
            total_copies = int(data["total_copies"])
            if total_copies < issued:
                raise ValueError("Total copies cannot be less than the number currently issued.")
            book.title = str(data["title"])
            book.author = str(data["author"])
            book.isbn = str(data["isbn"])
            book.total_copies = total_copies
            book.available_copies = total_copies - issued
            return book

    def delete_book(self, book_id: int) -> bool:
        with self._lock:
            book = self._books.get(book_id)
            if book is None or book.available_copies != book.total_copies:
                return False
            del self._books[book_id]
            return True

    def create_member(self, data: dict[str, object]) -> Member:
        with self._lock:
            member = Member(id=self._next_member_id, **data)
            self._members[member.id] = member
            self._next_member_id += 1
            return member

    def get_members(self) -> list[Member]:
        with self._lock:
            return list(self._members.values())

    def get_member(self, member_id: int) -> Member | None:
        with self._lock:
            return self._members.get(member_id)

    def update_member(self, member_id: int, data: dict[str, object]) -> Member | None:
        with self._lock:
            member = self._members.get(member_id)
            if member is None:
                return None
            member.name = str(data["name"])
            member.email = str(data["email"])
            member.membership_number = str(data["membership_number"])
            return member

    def delete_member(self, member_id: int) -> bool:
        with self._lock:
            if member_id not in self._members:
                return False
            active = any(loan.member_id == member_id and loan.returned_at is None for loan in self._loans.values())
            if active:
                return False
            del self._members[member_id]
            return True

    def isbn_exists(self, isbn: str) -> bool:
        with self._lock:
            return any(book.isbn.lower() == isbn.lower() for book in self._books.values())

    def email_exists(self, email: str) -> bool:
        with self._lock:
            return any(member.email.lower() == email.lower() for member in self._members.values())

    def membership_exists(self, membership_number: str) -> bool:
        with self._lock:
            return any(member.membership_number.lower() == membership_number.lower() for member in self._members.values())

    def issue_book(self, data: dict[str, object]) -> Loan:
        with self._lock:
            book = self._books.get(int(data["book_id"]))
            member = self._members.get(int(data["member_id"]))
            if book is None or member is None or book.available_copies <= 0:
                raise LookupError
            loan = Loan(
                id=self._next_loan_id,
                issued_at=datetime.now(),
                **data,
            )
            book.available_copies -= 1
            self._loans[loan.id] = loan
            self._next_loan_id += 1
            return loan

    def get_loans(self) -> list[Loan]:
        with self._lock:
            return list(self._loans.values())

    def return_book(self, loan_id: int) -> Loan | None:
        with self._lock:
            loan = self._loans.get(loan_id)
            if loan is None or loan.returned_at is not None:
                return None
            loan.returned_at = datetime.now()
            self._books[loan.book_id].available_copies += 1
            return loan

    def clear(self) -> None:
        with self._lock:
            self._books.clear()
            self._members.clear()
            self._loans.clear()
            self._next_book_id = 1
            self._next_member_id = 1
            self._next_loan_id = 1


library_service = LibraryService()
