import asyncio
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserLoginRequest

async def test():
    async with AsyncSessionLocal() as db:
        s = AuthService(db)
        try:
            res = await s.login(UserLoginRequest(email="test@example.com", password="Password123!"))
            print("Login success:", res)
        except Exception as e:
            print("Login error traceback:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
