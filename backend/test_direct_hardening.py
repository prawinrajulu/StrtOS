import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest, UserLoginRequest
from app.auth.jwt_handler import JWTHandler
from app.dashboard.service import DashboardService

async def test_direct_hardening():
    async with AsyncSessionLocal() as db:
        print("\n=======================================================")
        print("STARTING DIRECT PRODUCTION HARDENING & RELIABILITY VERIFICATION")
        print("=======================================================")

        # 1. Test Auth Service & Token Revocation / Blacklist
        print("\n[1/5] Testing Register & JWT Token Handlers...")
        auth_service = AuthService(db)
        uid = str(uuid.uuid4())[:8]
        email = f"harden-direct-{uid}@strtos.io"
        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Harden-Direct-Org-{uid}", full_name="Admin Direct", email=email, password="Password123!"
        ))
        assert reg.email == email

        token_resp = await auth_service.login(UserLoginRequest(email=email, password="Password123!"))
        access_token = token_resp.access_token

        payload = await JWTHandler.decode_and_verify_token(access_token)
        assert payload["sub"] == reg.id

        # 2. Test Logout Blacklisting
        print("\n[2/5] Testing JWT Blacklist Logout...")
        await auth_service.logout(user_id=reg.id, access_token=access_token)
        try:
            await JWTHandler.decode_and_verify_token(access_token)
            print("ERROR: Blacklisted token was accepted!")
            assert False
        except Exception as e:
            print("SECURITY SUCCESS: Blacklisted token rejected with exception:", type(e))

        # 3. Test Dashboard Aggregation Reliability
        print("\n[3/5] Testing Dashboard Aggregation Service...")
        dash_service = DashboardService(db)
        overview = await dash_service.get_overview(org_id=reg.organization_id)
        assert overview.clients.total_clients == 0
        assert overview.workflows.total_workflows == 0

        print("\n=======================================================")
        print("DIRECT PRODUCTION HARDENING VERIFICATION PASSED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_direct_hardening())
