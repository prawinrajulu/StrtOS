from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.models.database import User, Organization

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalars().first()

class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        result = await self.session.execute(select(Organization).filter(Organization.slug == slug))
        return result.scalars().first()
