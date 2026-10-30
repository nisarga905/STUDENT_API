from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.schemas.member import MemberCreate, MemberResponse, MemberUpdate
from app.services.library_service import library_service


router = APIRouter()


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate) -> MemberResponse:
    if library_service.email_exists(payload.email):
        raise HTTPException(status_code=409, detail="A member with this email already exists.")
    if library_service.membership_exists(payload.membership_number):
        raise HTTPException(status_code=409, detail="This membership number is already in use.")
    return MemberResponse(**asdict(library_service.create_member(payload.model_dump())))


@router.get("", response_model=list[MemberResponse])
def list_members() -> list[MemberResponse]:
    return [MemberResponse(**asdict(member)) for member in library_service.get_members()]


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int) -> MemberResponse:
    member = library_service.get_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} was not found.")
    return MemberResponse(**asdict(member))


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, payload: MemberUpdate) -> MemberResponse:
    member = library_service.update_member(member_id, payload.model_dump())
    if member is None:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} was not found.")
    return MemberResponse(**asdict(member))


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int) -> None:
    if not library_service.delete_member(member_id):
        raise HTTPException(status_code=409, detail="Member does not exist or has active loans.")
