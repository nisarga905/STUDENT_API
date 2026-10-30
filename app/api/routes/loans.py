from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.schemas.loan import LoanCreate, LoanResponse
from app.services.library_service import library_service


router = APIRouter()


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def issue_book(payload: LoanCreate) -> LoanResponse:
    if library_service.get_book(payload.book_id) is None:
        raise HTTPException(status_code=404, detail="Book was not found.")
    if library_service.get_member(payload.member_id) is None:
        raise HTTPException(status_code=404, detail="Member was not found.")
    book = library_service.get_book(payload.book_id)
    if book is not None and book.available_copies <= 0:
        raise HTTPException(status_code=409, detail="No copies of this book are available.")
    return LoanResponse(**asdict(library_service.issue_book(payload.model_dump())))


@router.get("", response_model=list[LoanResponse])
def list_loans() -> list[LoanResponse]:
    return [LoanResponse(**asdict(loan)) for loan in library_service.get_loans()]


@router.post("/{loan_id}/return", response_model=LoanResponse)
def return_book(loan_id: int) -> LoanResponse:
    loan = library_service.return_book(loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan was not found or has already been returned.")
    return LoanResponse(**asdict(loan))
