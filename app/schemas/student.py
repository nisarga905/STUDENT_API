from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=1, le=120)
    course: str = Field(min_length=1, max_length=100)


class StudentResponse(StudentCreate):
    id: int
