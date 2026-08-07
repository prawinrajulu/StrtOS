from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository, OrganizationRepository
from app.models.database import User, Organization
from app.schemas.all_schemas import UserCreate, LoginRequest, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import AuthenticationException, ValidationException

class AuthService:
    """
    Service Layer handling User Authentication & Registration business logic.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)

    async def register_user(self, user_in: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ValidationException("User with this email already exists")

        # Get or create default Enterprise organization
        org_id = user_in.organization_id
        if not org_id:
            org = await self.org_repo.get_by_slug("arcadia-ventures")
            if not org:
                org = Organization(name="Arcadia Ventures", slug="arcadia-ventures", tier="ENTERPRISE")
                org = await self.org_repo.create(org)
            org_id = org.id

        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role=user_in.role,
            organization_id=org_id
        )
        return await self.user_repo.create(user)

    async def authenticate_user(self, login_in: LoginRequest) -> Token:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise AuthenticationException("Incorrect email or password")

        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token, token_type="bearer")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
