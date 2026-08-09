import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.auth.models import OrganizationModel, UserModel, UserRole, UserStatus
from app.auth.service import security_handler

async def debug():
    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        org = OrganizationModel(name=f"Debug Org {uid}", slug=f"debug-org-{uid}")
        db.add(org)
        await db.flush()

        user = UserModel(
            organization_id=org.id,
            full_name="Debug User",
            email=f"debug-{uid}@test.com",
            password_hash=security_handler.hash_password("Password123!"),
            role=UserRole.ORG_ADMIN,
            status=UserStatus.ACTIVE
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        print(f"Created Org ID: {org.id}, User ID: {user.id}")

        service = ClientService(db)
        try:
            client = await service.create_client(
                payload=ClientCreateRequest(
                    name="Apex Health Solutions",
                    industry="HealthTech",
                    website_url="https://apexhealth.io",
                    business_goal="Scale telemedicine user acquisition by 45% in Q4.",
                    monthly_budget=25000,
                    currency="USD"
                ),
                org_id=org.id,
                creator_id=user.id
            )
            print("Successfully created client:", client)
        except Exception as e:
            print("Create client error:", type(e), e)

if __name__ == "__main__":
    asyncio.run(debug())
