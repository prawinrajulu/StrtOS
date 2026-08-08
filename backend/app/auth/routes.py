from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserDTO,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest,
    ChangePasswordRequest, UserSessionDTO
)
from app.auth.service import AuthService
from app.auth.dependencies import get_current_user
from app.auth.models import UserModel
from app.schemas.all_schemas import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Enterprise Auth & RBAC"])

@router.post("/register", response_model=SuccessResponse[UserDTO], status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Registers a new Organization & Organization Admin user."""
    service = AuthService(db)
    user_dto = await service.register_organization(payload, ip_address=request.client.host if request.client else None)
    return SuccessResponse(data=user_dto, message="Organization registered successfully.")

@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(payload: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticates user and returns JWT Access & Refresh Tokens."""
    service = AuthService(db)
    token_resp = await service.login(
        payload,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    return SuccessResponse(data=token_resp, message="Login successful.")

@router.post("/logout", response_model=SuccessResponse[dict])
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logs out user, invalidates session, revokes refresh tokens, and blacklists JWT."""
    token = authorization.split(" ")[1] if authorization and "Bearer " in authorization else ""
    service = AuthService(db)
    await service.logout(current_user.id, token, ip_address=request.client.host if request.client else None)
    return SuccessResponse(data={"status": "logged_out"}, message="Logged out successfully.")

@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refreshes access token and rotates refresh token."""
    service = AuthService(db)
    tokens = await service.refresh_tokens(payload.refresh_token)
    return SuccessResponse(data=tokens, message="Tokens refreshed successfully.")

@router.post("/forgot-password", response_model=SuccessResponse[dict])
async def forgot_password(payload: ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Generates password reset token."""
    service = AuthService(db)
    reset_token = await service.forgot_password(payload.email, ip_address=request.client.host if request.client else None)
    return SuccessResponse(data={"reset_token": reset_token}, message="Password reset token generated.")

@router.post("/reset-password", response_model=SuccessResponse[dict])
async def reset_password(payload: ResetPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Resets password using reset token."""
    service = AuthService(db)
    await service.reset_password(payload.reset_token, payload.new_password, ip_address=request.client.host if request.client else None)
    return SuccessResponse(data={"status": "password_reset"}, message="Password reset successfully.")

@router.post("/change-password", response_model=SuccessResponse[dict])
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Changes password for authenticated user."""
    service = AuthService(db)
    await service.change_password(current_user.id, payload.current_password, payload.new_password, ip_address=request.client.host if request.client else None)
    return SuccessResponse(data={"status": "password_changed"}, message="Password changed successfully.")

@router.get("/me", response_model=SuccessResponse[UserDTO])
async def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Returns profile for currently authenticated user."""
    user_dto = UserDTO(
        id=current_user.id,
        organization_id=current_user.organization_id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        status=current_user.status,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )
    return SuccessResponse(data=user_dto, message="Profile fetched.")

@router.get("/sessions", response_model=SuccessResponse[List[UserSessionDTO]])
async def get_sessions(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Returns active user sessions."""
    service = AuthService(db)
    sessions = await service.get_user_sessions(current_user.id)
    return SuccessResponse(data=sessions, message="Sessions fetched.")

@router.delete("/session/{session_id}", response_model=SuccessResponse[dict])
async def revoke_session(session_id: str, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Revokes a specific session."""
    service = AuthService(db)
    await service.revoke_session(session_id, current_user.id)
    return SuccessResponse(data={"revoked_session_id": session_id}, message="Session revoked successfully.")
