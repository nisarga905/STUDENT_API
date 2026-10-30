from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str = Field(min_length=1, max_length=20)
    total_copies: int = Field(gt=0)


class BookUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str = Field(min_length=1, max_length=20)
    total_copies: int = Field(gt=0)


class BookResponse(BookCreate):
    id: int
    available_copies: int
