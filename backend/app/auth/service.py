import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserDTO, UserSessionDTO
)
from app.auth.models import UserRole, UserStatus
from app.auth.repository import AuthRepository
from app.auth.security import security_handler
from app.auth.jwt_handler import jwt_handler
from app.auth.validator import AuthValidator
from app.auth.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException, AuthException, InvalidTokenException
)

class AuthService:
    """Core Enterprise Authentication & Multi-Tenant Authorization Service."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AuthRepository(session)

    async def register_organization(self, payload: UserRegisterRequest, ip_address: Optional[str] = None) -> UserDTO:
        AuthValidator.validate_password(payload.password)

        existing_user = await self.repo.get_user_by_email(payload.email)
        if existing_user:
            raise UserAlreadyExistsException()

        slug = payload.organization_name.lower().replace(" ", "-")
        org = await self.repo.create_organization(payload.organization_name, slug)
        pwd_hash = security_handler.hash_password(payload.password)
        
        user = await self.repo.create_user(
            org_id=org.id,
            full_name=payload.full_name,
            email=payload.email,
            password_hash=pwd_hash,
            role=UserRole.ORG_ADMIN,
            phone=payload.phone
        )

        await self.repo.log_audit("USER_REGISTER", user.id, org.id, {"email": user.email}, ip_address)
        await self.session.commit()

        return UserDTO(
            id=user.id,
            organization_id=user.organization_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            status=user.status,
            is_verified=user.is_verified,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at
        )

    async def login(self, payload: UserLoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        user = await self.repo.get_user_by_email(payload.email)
        if not user or not security_handler.verify_password(payload.password, user.password_hash):
            if user:
                await self.repo.log_audit("FAILED_LOGIN", user.id, user.organization_id, {"email": payload.email}, ip_address)
                await self.session.commit()
            raise InvalidCredentialsException()

        if not user.is_active or user.status != UserStatus.ACTIVE:
            raise AuthException("User account is inactive or suspended.")

        user.last_login = datetime.now(timezone.utc)
        
        access_token = jwt_handler.create_access_token(user.id, user.organization_id, user.role.value)
        refresh_token = jwt_handler.create_refresh_token(user.id)

        exp = datetime.now(timezone.utc) + timedelta(days=7)
        await self.repo.save_refresh_token(user.id, refresh_token, exp)
        await self.repo.create_session(user.id, ip_address, user_agent)
        await self.repo.log_audit("USER_LOGIN", user.id, user.organization_id, {"email": user.email}, ip_address)
        await self.session.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, old_refresh_token: str) -> TokenResponse:
        payload = await jwt_handler.decode_and_verify_token(old_refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenException()

        db_token = await self.repo.get_refresh_token(old_refresh_token)
        if not db_token or db_token.is_revoked or db_token.expires_at < datetime.now(timezone.utc):
            raise InvalidTokenException()

        # Revoke previous token (Token Rotation)
        await self.repo.revoke_refresh_token(old_refresh_token)

        user = await self.repo.get_user_by_id(db_token.user_id)
        if not user or not user.is_active:
            raise AuthException("User inactive.")

        new_access_token = jwt_handler.create_access_token(user.id, user.organization_id, user.role.value)
        new_refresh_token = jwt_handler.create_refresh_token(user.id)

        exp = datetime.now(timezone.utc) + timedelta(days=7)
        await self.repo.save_refresh_token(user.id, new_refresh_token, exp)
        await self.session.commit()

        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)

    async def logout(self, user_id: str, access_token: str, ip_address: Optional[str] = None):
        await jwt_handler.blacklist_token(access_token)
        await self.repo.deactivate_user_sessions(user_id)
        await self.repo.revoke_all_user_refresh_tokens(user_id)
        await self.repo.log_audit("USER_LOGOUT", user_id, None, {}, ip_address)
        await self.session.commit()

    async def forgot_password(self, email: str, ip_address: Optional[str] = None) -> str:
        user = await self.repo.get_user_by_email(email)
        if not user:
            return "reset_token_sent"  # Prevent timing attacks

        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        await self.repo.create_password_reset_token(user.id, token_hash, expires_at)
        await self.repo.log_audit("FORGOT_PASSWORD_REQUEST", user.id, user.organization_id, {}, ip_address)
        await self.session.commit()
        return reset_token

    async def reset_password(self, reset_token: str, new_password: str, ip_address: Optional[str] = None):
        AuthValidator.validate_password(new_password)
        token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()

        prt = await self.repo.get_password_reset_token(token_hash)
        if not prt or prt.is_used or prt.expires_at < datetime.now(timezone.utc):
            raise AuthException("Invalid or expired password reset token.")

        user = await self.repo.get_user_by_id(prt.user_id)
        if not user:
            raise AuthException("User not found.")

        user.password_hash = security_handler.hash_password(new_password)
        await self.repo.mark_password_reset_token_used(prt.id)
        await self.repo.deactivate_user_sessions(user.id)
        await self.repo.revoke_all_user_refresh_tokens(user.id)

        await self.repo.log_audit("PASSWORD_RESET_SUCCESS", user.id, user.organization_id, {}, ip_address)
        await self.session.commit()

    async def change_password(self, user_id: str, current_password: str, new_password: str, ip_address: Optional[str] = None):
        AuthValidator.validate_password(new_password)
        user = await self.repo.get_user_by_id(user_id)
        if not user or not security_handler.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsException()

        user.password_hash = security_handler.hash_password(new_password)
        await self.repo.revoke_all_user_refresh_tokens(user.id)
        await self.repo.log_audit("PASSWORD_CHANGE_SUCCESS", user.id, user.organization_id, {}, ip_address)
        await self.session.commit()

    async def get_user_sessions(self, user_id: str) -> List[UserSessionDTO]:
        sessions = await self.repo.get_user_sessions(user_id)
        return [
            UserSessionDTO(
                id=s.id,
                user_id=s.user_id,
                ip_address=s.ip_address,
                user_agent=s.user_agent,
                is_active=s.is_active,
                last_activity=s.last_activity,
                created_at=s.created_at
            ) for s in sessions
        ]

    async def revoke_session(self, session_id: str, user_id: str):
        await self.repo.deactivate_session(session_id, user_id)
        await self.session.commit()
