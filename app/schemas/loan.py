from datetime import datetime

from pydantic import BaseModel


class LoanCreate(BaseModel):
    book_id: int
    member_id: int
    due_at: datetime


class LoanResponse(LoanCreate):
    id: int
    issued_at: datetime
    returned_at: datetime | None = None
