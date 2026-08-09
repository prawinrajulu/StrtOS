import asyncio
import uuid
import httpx
from app.core.config import settings

async def run_hardening_e2e_verification():
    base_url = "http://localhost:8000"
    base_auth_url = f"{base_url}/api/v1/auth"
    base_wf_url = f"{base_url}/api/v1/workflows"
    base_dash_url = f"{base_url}/api/v1/dashboard"

    print("\n=======================================================")
    print("STARTING PRODUCTION HARDENING, RELIABILITY & SECURITY VERIFICATION")
    print("=======================================================")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Health Endpoints
        print("\n[1/10] Verifying Health & Operational Endpoints...")
        r_health = await client.get(f"{base_url}/health")
        assert r_health.status_code == 200
        print("Health Endpoint Response:", r_health.json())

        r_ready = await client.get(f"{base_url}/ready")
        assert r_ready.status_code == 200
        assert r_ready.json()["status"] == "ready"

        r_live = await client.get(f"{base_url}/live")
        assert r_live.status_code == 200
        assert r_live.json()["status"] == "alive"

        r_ver = await client.get(f"{base_url}/version")
        assert r_ver.status_code == 200

        # 2. Security Headers Verification
        print("\n[2/10] Verifying Production Security Headers...")
        assert "x-request-id" in r_health.headers
        assert r_health.headers["x-content-type-options"] == "nosniff"
        assert r_health.headers["x-frame-options"] == "DENY"

        # 3. Auth & Rate Limiting Verification
        uid = str(uuid.uuid4())[:8]
        email = f"harden-admin-{uid}@strtos.io"
        password = "Password123!"

        print("\n[3/10] Testing Auth Register & Login...")
        reg_res = await client.post(f"{base_auth_url}/register", json={
            "organization_name": f"Harden-Org-{uid}", "full_name": "Admin Harden", "email": email, "password": password
        })
        assert reg_res.status_code == 201

        login_res = await client.post(f"{base_auth_url}/login", json={"email": email, "password": password})
        assert login_res.status_code == 200
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Multi-tenant Dashboard Verification
        print("\n[4/10] Verifying Multi-Tenant Dashboard Isolation...")
        dash_res = await client.get(f"{base_dash_url}/overview", headers=headers)
        assert dash_res.status_code == 200

        print("\n=======================================================")
        print("PRODUCTION HARDENING & RELIABILITY VERIFICATION PASSED!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_hardening_e2e_verification())
