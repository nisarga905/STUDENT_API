from fastapi import FastAPI

from app.api.routes import students


app = FastAPI(
    title="Student API",
    description="Backend API for managing student records.",
    version="1.0.0",
)

app.include_router(students.router, prefix="/api/students", tags=["Students"])
