from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.schemas.library import (
    BookCreate,
    BookResponse,
    LoanCreate,
    LoanResponse,
    ReservationCreate,
    ReservationResponse,
)
from app.services.library_service import LibraryError, library_service


router = APIRouter()


def raise_library_error(error: LibraryError) -> None:
    raise HTTPException(status_code=error.status_code, detail=error.detail)


def loan_response(loan) -> LoanResponse:
    return LoanResponse(**asdict(loan), fine=library_service.calculate_fine(loan))


def book_response(book) -> BookResponse:
    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        total_copies=library_service.total_copies(book.id),
        available_copies=book.available_copies,
    )


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(payload: BookCreate) -> BookResponse:
    try:
        return book_response(library_service.create_book(payload.model_dump()))
    except LibraryError as error:
        raise_library_error(error)


@router.get("/books", response_model=list[BookResponse])
def view_books() -> list[BookResponse]:
    return [book_response(book) for book in library_service.get_books()]


@router.post("/loans", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate) -> LoanResponse:
    try:
        return loan_response(library_service.borrow(payload.student_id, payload.book_id, payload.loan_days))
    except LibraryError as error:
        raise_library_error(error)


@router.post("/loans/{loan_id}/return", response_model=LoanResponse)
def return_loan(loan_id: int) -> LoanResponse:
    try:
        return loan_response(library_service.return_book(loan_id))
    except LibraryError as error:
        raise_library_error(error)


@router.get("/loans/overdue", response_model=list[LoanResponse])
def view_overdue_loans() -> list[LoanResponse]:
    return [
        loan_response(loan)
        for loan in library_service.get_loans()
        if loan.returned_at is None and library_service.calculate_fine(loan) > 0
    ]


@router.get("/loans", response_model=list[LoanResponse])
def view_loans() -> list[LoanResponse]:
    return [loan_response(loan) for loan in library_service.get_loans()]


@router.get("/students/{student_id}/loans", response_model=list[LoanResponse])
def view_student_loans(student_id: int) -> list[LoanResponse]:
    try:
        return [loan_response(loan) for loan in library_service.get_student_loans(student_id)]
    except LibraryError as error:
        raise_library_error(error)


@router.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate) -> ReservationResponse:
    try:
        return ReservationResponse(**asdict(library_service.reserve(payload.student_id, payload.book_id)))
    except LibraryError as error:
        raise_library_error(error)


@router.get("/reservations", response_model=list[ReservationResponse])
def view_reservations(student_id: int | None = None) -> list[ReservationResponse]:
    return [
        ReservationResponse(**asdict(reservation))
        for reservation in library_service.get_reservations(student_id)
    ]


@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(reservation_id: int) -> None:
    try:
        if not library_service.cancel_reservation(reservation_id):
            raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} was not found.")
    except LibraryError as error:
        raise_library_error(error)
