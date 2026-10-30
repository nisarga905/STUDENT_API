from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.schemas.student import StudentCreate, StudentResponse
from app.services.student_service import student_service


router = APIRouter()


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_student(payload: StudentCreate) -> StudentResponse:
    """Create a student record."""
    if student_service.email_exists(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        )

    return StudentResponse(**asdict(student_service.create(payload.model_dump())))


@router.get("", response_model=list[StudentResponse])
def view_students() -> list[StudentResponse]:
    """Return every student record."""
    return [
        StudentResponse(**asdict(student))
        for student in student_service.get_all()
    ]


@router.get("/{student_id}", response_model=StudentResponse)
def view_student(student_id: int) -> StudentResponse:
    """Return one student by ID."""
    student = student_service.get_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} was not found.",
        )

    return StudentResponse(**asdict(student))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int) -> None:
    """Delete one student by ID."""
    if not student_service.delete(student_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} was not found.",
        )
