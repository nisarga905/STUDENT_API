from fastapi import FastAPI

from app.api.routes import library, students


app = FastAPI(
    title="Student API",
    description="Backend API for managing student records and library services.",
    version="1.0.0",
)

app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(library.router, prefix="/api/library", tags=["Library"])
