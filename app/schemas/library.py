from datetime import datetime

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str = Field(min_length=1, max_length=20)
    copies: int = Field(ge=1)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int


class LoanCreate(BaseModel):
    student_id: int = Field(gt=0)
    book_id: int = Field(gt=0)
    loan_days: int = Field(default=14, ge=1, le=365)


class LoanResponse(BaseModel):
    id: int
    student_id: int
    book_id: int
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None
    fine: float = 0


class ReservationCreate(BaseModel):
    student_id: int = Field(gt=0)
    book_id: int = Field(gt=0)


class ReservationResponse(BaseModel):
    id: int
    student_id: int
    book_id: int
    created_at: datetime
    status: str
