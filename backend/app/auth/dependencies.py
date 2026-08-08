from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.jwt_handler import jwt_handler
from app.auth.repository import AuthRepository
from app.auth.models import UserModel, UserRole
from app.auth.exceptions import AccessDeniedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserModel:
    payload = await jwt_handler.decode_and_verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")
    
    repo = AuthRepository(db)
    user = await repo.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
    return user

async def get_current_organization_id(current_user: UserModel = Depends(get_current_user)) -> str:
    return current_user.organization_id

class RoleChecker:
    """Dependency enforcing Role-Based Access Control (RBAC)."""
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserModel = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise AccessDeniedException(f"Role '{current_user.role.value}' is not authorized to perform this operation.")
        return current_user
