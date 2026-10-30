from dataclasses import dataclass
from datetime import datetime


@dataclass
class Loan:
    id: int
    book_id: int
    member_id: int
    issued_at: datetime
    due_at: datetime
    returned_at: datetime | None = None
