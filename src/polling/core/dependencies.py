from collections.abc import Callable
from typing import Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polling.core.config import core
from polling.database import get_db
from polling.models.users import User

oauth2_scheme = HTTPBearer()

#     try:
#         payload = jwt.decode(
#             token,
#             core.jwt_secret_key,
#             algorithms=[core.jwt_algorithm],
#         )

#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")

#     user_id = payload.get("sub")

#     if user_id is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

#     result = await db.execute(select(User).where(User.id == int(user_id)))
#     user = result.scalar_one_or_none()

#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")

#     if not user.is_active:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User account is inactive")

#     return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),db: AsyncSession = Depends(get_db),) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            core.jwt_secret_key,
            algorithms=[core.jwt_algorithm],
        )

        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)

    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User account is inactive")

    return user

def require_roles(*allowed_roles: str):

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Insufficient permissions")

        return current_user

    return role_checker
