import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from polling.core.config import core

from polling.core.dependencies import get_current_user
from polling.core.dependencies import oauth2_scheme
from polling.database import get_db
from polling.models.users import User
from polling.schema.auth import LoginRequest, RegisterRequest,TokenResponse
from polling.core.security import (
    create_access_token,
    verify_password,
    hash_password
)
from polling.core.rate_limit import limiter
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/auth",tags=["Authentication"])


async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin Access is required")
    return current_user


@router.post("/login",response_model=TokenResponse)
@limiter.limit("2/minute")
@limiter.limit("3/hour")
@limiter.limit("5/day")
async def login(request: Request, data: LoginRequest,db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.username == data.username))

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")

    if not verify_password(data.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User account is inactive")

    access_token = create_access_token(user_id=user.id,role=user.role)
    return TokenResponse(access_token=access_token,)


@router.post('/register', response_model=TokenResponse,  dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.MINUTE * 60))))])
async def register(data: RegisterRequest,db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    
    print("Registering new user:", data.username, "with role:", data.role, "and password:", data.password)  # Debugging line
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Username already exists",)
    new_user = User(
        name=data.name,
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(user_id=new_user.id, role=new_user.role)
    return TokenResponse(access_token=access_token)


@router.get("/adminpanel")
async def get_admin_panel(current_user: User = Depends(require_admin)):
    return {
        "message": "Welcome to Admin Panel",
        "username": current_user.username,
        "role": current_user.role,
    }