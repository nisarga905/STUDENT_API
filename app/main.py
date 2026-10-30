from fastapi import FastAPI

from app.api.routes import books, loans, members, students


app = FastAPI(
    title="Student and Library API",
    description="Backend API for managing student records and library operations.",
    version="1.1.0",
)

app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
app.include_router(members.router, prefix="/api/members", tags=["Members"])
app.include_router(loans.router, prefix="/api/loans", tags=["Loans"])
