from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.services.library_service import library_service


router = APIRouter()


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate) -> BookResponse:
    if library_service.isbn_exists(payload.isbn):
        raise HTTPException(status_code=409, detail="A book with this ISBN already exists.")
    return BookResponse(**asdict(library_service.create_book(payload.model_dump())))


@router.get("", response_model=list[BookResponse])
def list_books() -> list[BookResponse]:
    return [BookResponse(**asdict(book)) for book in library_service.get_books()]


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int) -> BookResponse:
    book = library_service.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} was not found.")
    return BookResponse(**asdict(book))


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate) -> BookResponse:
    try:
        book = library_service.update_book(book_id, payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} was not found.")
    return BookResponse(**asdict(book))


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int) -> None:
    if not library_service.delete_book(book_id):
        raise HTTPException(status_code=409, detail="Book is unavailable or has been issued and cannot be deleted.")
