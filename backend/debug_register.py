import asyncio
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest

async def test():
    async with AsyncSessionLocal() as db:
        s = AuthService(db)
        try:
            res = await s.register_organization(UserRegisterRequest(
                organization_name="Test Org",
                full_name="Test User",
                email="testadmin@example.com",
                password="Password123!"
            ))
            print("Registration Success:", res)
        except Exception as e:
            print("Registration error:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
