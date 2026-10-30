from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
