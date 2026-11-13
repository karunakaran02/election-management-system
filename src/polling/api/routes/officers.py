from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polling.core.dependencies import require_roles
from polling.database import get_db
from polling.models.users import User
from polling.models import PollingOfficer
from polling.schema.officers import OfficerCreateRequest, OfficerResponse, OfficerPutRequest, OfficerPatchRequest
from polling.core.security import hash_password

router = APIRouter(
    prefix="/officer",
    tags=["Polling Officer"],
)


@router.get("/")
async def get_officer(current_user: User = Depends(require_roles("admin")), db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(PollingOfficer).where(PollingOfficer.user_id == current_user.id))
    officer = result.scalar_one_or_none()

    if officer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Polling officer record not found",)

    return {
        "id": officer.id,
        "user_id": officer.user_id,
        "employee_code": officer.employee_code,
        "created_at": officer.created_at,
    }


@router.post("registerOfficers",response_model=OfficerResponse,status_code=status.HTTP_201_CREATED)
async def create_officer(data: OfficerCreateRequest,current_user: User = Depends(require_roles("admin")),db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User).where(User.username == data.username))
    existing_user = result.scalar_one_or_none() 

    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Username already exists")

    result = await db.execute(select(PollingOfficer).where(PollingOfficer.employee_code == data.employee_code))

    existing_officer = result.scalar_one_or_none()

    if existing_officer is not None:
        raise HTTPException( status_code=status.HTTP_409_CONFLICT,detail="Employee code already exists")

    new_user = User(
        name=data.name,
        username=data.username,
        password_hash=hash_password(data.password),
        role="polling_officer",
        is_active=True,
    )

    db.add(new_user)

    await db.flush()

    new_officer = PollingOfficer(
        user_id=new_user.id,
        employee_code=data.employee_code,
    )

    db.add(new_officer)

    await db.commit()

    await db.refresh(new_user)
    await db.refresh(new_officer)

    return OfficerResponse(
        id=new_officer.id,
        user_id=new_user.id,
        name=new_user.name,
        username=new_user.username,
        employee_code=new_officer.employee_code,
        role=new_user.role,
        created_at=new_officer.created_at,
    )

@router.delete("/{officer_id}")
async def delete_officer( officer_id: int,current_user: User = Depends(require_roles("admin")),db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(PollingOfficer).where(PollingOfficer.id == officer_id))
    officer = result.scalar_one_or_none()

    if officer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Polling officer not found")

    result = await db.execute(select(User).where(User.id == officer.user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated user not found")

    user.is_active = False
    await db.commit()

    return {
        "message": "Polling officer deactivated successfully",
        "officer_id": officer.id,
        "user_id": user.id,
        "is_active": user.is_active,
    }


@router.put("/{officer_id}")
async def update_officer(officer_id: int,data: OfficerPutRequest,current_user: User = Depends(require_roles("admin")),db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PollingOfficer).where(PollingOfficer.id == officer_id))

    officer = result.scalar_one_or_none()

    if officer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Polling officer not found")

    result = await db.execute(select(User).where(User.id == officer.user_id))

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Associated user not found")

    result = await db.execute(select(User).where(User.username == data.username,User.id != user.id))

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Username already exists")

    result = await db.execute(select(PollingOfficer).where(PollingOfficer.employee_code == data.employee_code,PollingOfficer.id != officer.id,))

    existing_officer = result.scalar_one_or_none()

    if existing_officer is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Employee code already exists")

    user.name = data.name
    user.username = data.username

    officer.employee_code = data.employee_code

    await db.commit()

    await db.refresh(user)
    await db.refresh(officer)

    return {
        "message": "Polling officer updated successfully",
        "officer_id": officer.id,
        "user_id": user.id,
        "name": user.name,
        "username": user.username,
        "employee_code": officer.employee_code,
    }


@router.patch("/{officer_id}")
async def patch_officer(officer_id: int,data: OfficerPatchRequest,current_user: User = Depends(require_roles("admin")),db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PollingOfficer).where(PollingOfficer.id == officer_id))

    officer = result.scalar_one_or_none()

    if officer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Polling officer not found")

    result = await db.execute(select(User).where(User.id == officer.user_id))

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Associated user not found")

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="At least one field must be provided")

    if "username" in update_data:
        result = await db.execute(select(User).where(User.username == update_data["username"],User.id != user.id))

        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Username already exists")

    if "employee_code" in update_data:
        result = await db.execute(select(PollingOfficer).where( PollingOfficer.employee_code == update_data["employee_code"],PollingOfficer.id != officer.id))

        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Employee code already exists",)

    if "name" in update_data:
        user.name = update_data["name"]

    if "username" in update_data:
        user.username = update_data["username"]

    if "employee_code" in update_data:
        officer.employee_code = update_data["employee_code"]

    await db.commit()

    await db.refresh(user)
    await db.refresh(officer)

    return {
        "message": "Polling officer updated successfully",
        "officer_id": officer.id,
        "user_id": user.id,
        "name": user.name,
        "username": user.username,
        "employee_code": officer.employee_code,
    }