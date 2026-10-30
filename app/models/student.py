from dataclasses import dataclass


@dataclass(slots=True)
class Student:
    id: int
    name: str
    email: str
    age: int
    course: str
