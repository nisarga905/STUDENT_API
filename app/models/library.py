from dataclasses import dataclass
from datetime import datetime


@dataclass
class Book:
    id: int
    title: str
    author: str
    isbn: str
    available_copies: int


@dataclass
class Loan:
    id: int
    book_id: int
    student_id: int
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None = None


@dataclass
class Reservation:
    id: int
    book_id: int
    student_id: int
    created_at: datetime
    status: str = "active"
