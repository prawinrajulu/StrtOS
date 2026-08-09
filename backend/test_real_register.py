import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest

async def test():
    uid = str(uuid.uuid4())[:8]
    email = f"admin-{uid}@test.com"
    org_name = f"Org-{uid}"
    print(f"Attempting registration with email: {email}, org: {org_name}")
    async with AsyncSessionLocal() as db:
        service = AuthService(db)
        try:
            res = await service.register_organization(UserRegisterRequest(
                organization_name=org_name,
                full_name="Test Admin",
                email=email,
                password="Password123!"
            ))
            print("REGISTRATION SUCCESSFUL:", res)
        except Exception as e:
            print("REGISTRATION EXCEPTION:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test())
