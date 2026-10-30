from pydantic import BaseModel, EmailStr, Field


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    membership_number: str = Field(min_length=1, max_length=50)


class MemberUpdate(MemberCreate):
    pass


class MemberResponse(MemberCreate):
    id: int
