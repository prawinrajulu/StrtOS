from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.auth.models import (
    OrganizationModel, UserModel, RefreshTokenModel,
    UserSessionModel, PasswordResetTokenModel, AuditLogModel, UserRole
)

class AuthRepository:
    """Async Repository for Database Persistence Operations."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalars().first()

    async def create_organization(self, name: str, slug: str) -> OrganizationModel:
        org = OrganizationModel(name=name, slug=slug)
        self.session.add(org)
        await self.session.flush()
        return org

    async def create_user(
        self,
        org_id: str,
        full_name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.ORG_ADMIN,
        phone: Optional[str] = None
    ) -> UserModel:
        user = UserModel(
            organization_id=org_id,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role=role,
            phone=phone
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def save_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> RefreshTokenModel:
        rt = RefreshTokenModel(user_id=user_id, token=token, expires_at=expires_at)
        self.session.add(rt)
        await self.session.flush()
        return rt

    async def get_refresh_token(self, token: str) -> Optional[RefreshTokenModel]:
        result = await self.session.execute(select(RefreshTokenModel).where(RefreshTokenModel.token == token, RefreshTokenModel.is_revoked == False))
        return result.scalars().first()

    async def revoke_refresh_token(self, token: str):
        await self.session.execute(update(RefreshTokenModel).where(RefreshTokenModel.token == token).values(is_revoked=True))
        await self.session.flush()

    async def revoke_all_user_refresh_tokens(self, user_id: str):
        await self.session.execute(update(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id).values(is_revoked=True))
        await self.session.flush()

    async def create_session(self, user_id: str, ip_address: Optional[str], user_agent: Optional[str]) -> UserSessionModel:
        sess = UserSessionModel(user_id=user_id, ip_address=ip_address, user_agent=user_agent)
        self.session.add(sess)
        await self.session.flush()
        return sess

    async def deactivate_user_sessions(self, user_id: str):
        await self.session.execute(update(UserSessionModel).where(UserSessionModel.user_id == user_id).values(is_active=False))
        await self.session.flush()

    async def deactivate_session(self, session_id: str, user_id: str):
        await self.session.execute(update(UserSessionModel).where(UserSessionModel.id == session_id, UserSessionModel.user_id == user_id).values(is_active=False))
        await self.session.flush()

    async def get_user_sessions(self, user_id: str) -> List[UserSessionModel]:
        result = await self.session.execute(select(UserSessionModel).where(UserSessionModel.user_id == user_id, UserSessionModel.is_active == True))
        return list(result.scalars().all())

    async def create_password_reset_token(self, user_id: str, token_hash: str, expires_at: datetime) -> PasswordResetTokenModel:
        prt = PasswordResetTokenModel(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(prt)
        await self.session.flush()
        return prt

    async def get_password_reset_token(self, token_hash: str) -> Optional[PasswordResetTokenModel]:
        result = await self.session.execute(select(PasswordResetTokenModel).where(PasswordResetTokenModel.token_hash == token_hash, PasswordResetTokenModel.is_used == False))
        return result.scalars().first()

    async def mark_password_reset_token_used(self, token_id: str):
        await self.session.execute(update(PasswordResetTokenModel).where(PasswordResetTokenModel.id == token_id).values(is_used=True))
        await self.session.flush()

    async def log_audit(self, action: str, user_id: Optional[str], org_id: Optional[str], details: dict = None, ip_address: str = None):
        log = AuditLogModel(action=action, user_id=user_id, organization_id=org_id, details=details, ip_address=ip_address)
        self.session.add(log)
        await self.session.flush()
