from dataclasses import dataclass


@dataclass
class Member:
    id: int
    name: str
    email: str
    membership_number: str
