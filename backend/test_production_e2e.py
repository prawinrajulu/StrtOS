import asyncio
import uuid
import httpx

async def run_full_production_e2e():
    base_url = "http://localhost:8000"
    api_v1 = f"{base_url}/api/v1"

    uid_a = str(uuid.uuid4())[:8]
    email_a = f"prod-e2e-a-{uid_a}@strtos.io"
    org_a_name = f"Prod-Org-A-{uid_a}"

    uid_b = str(uuid.uuid4())[:8]
    email_b = f"prod-e2e-b-{uid_b}@globex.io"
    org_b_name = f"Prod-Org-B-{uid_b}"

    password = "Password123!"

    print("\n=======================================================")
    print("STARTING FULL SYSTEM PRODUCTION E2E SUITE")
    print("=======================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health, Readiness & Liveness
        print("\n[1/15] Verifying Production Operational Endpoints...")
        r_root = await client.get(f"{base_url}/")
        assert r_root.status_code == 200

        r_health = await client.get(f"{base_url}/health")
        assert r_health.status_code == 200

        r_ready = await client.get(f"{base_url}/ready")
        assert r_ready.status_code == 200
        assert r_ready.json()["status"] == "ready"

        r_live = await client.get(f"{base_url}/live")
        assert r_live.status_code == 200

        r_ver = await client.get(f"{base_url}/version")
        assert r_ver.status_code == 200

        # 2. CORS Preflight & Security Headers
        print("\n[2/15] Verifying CORS Preflight & Security Headers...")
        options_res = await client.options(f"{api_v1}/auth/login", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST"
        })
        assert options_res.status_code == 200
        assert "x-request-id" in r_health.headers
        assert r_health.headers["x-content-type-options"] == "nosniff"

        # 3. Register & Login Org A
        print(f"\n[3/15] Registering Org A ({email_a})...")
        reg_a = await client.post(f"{api_v1}/auth/register", json={
            "organization_name": org_a_name, "full_name": "Admin Org A", "email": email_a, "password": password
        })
        assert reg_a.status_code == 201

        login_a = await client.post(f"{api_v1}/auth/login", json={"email": email_a, "password": password})
        assert login_a.status_code == 200
        token_a = login_a.json()["data"]["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 4. Register & Login Org B
        print(f"\n[4/15] Registering Org B ({email_b})...")
        reg_b = await client.post(f"{api_v1}/auth/register", json={
            "organization_name": org_b_name, "full_name": "Admin Org B", "email": email_b, "password": password
        })
        assert reg_b.status_code == 201

        login_b = await client.post(f"{api_v1}/auth/login", json={"email": email_b, "password": password})
        token_b = login_b.json()["data"]["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 5. GET /auth/me
        print("\n[5/15] Fetching Authenticated User (/auth/me)...")
        me_res = await client.get(f"{api_v1}/auth/me", headers=headers_a)
        assert me_res.status_code == 200
        assert me_res.json()["data"]["email"] == email_a

        # 6. Create Client for Org A
        print("\n[6/15] Creating Enterprise Client for Org A...")
        c_res = await client.post(f"{api_v1}/clients", headers=headers_a, json={
            "name": "Starlight Corp", "industry": "Enterprise Software", "website_url": "https://starlight.io"
        })
        assert c_res.status_code == 201
        client_a_id = c_res.json()["data"]["id"]

        # 7. Create Workflow for Org A
        print("\n[7/15] Creating Workflow for Org A...")
        wf_res = await client.post(f"{api_v1}/workflows", headers=headers_a, json={
            "client_id": client_a_id, "title": "Starlight Market Expansion", "directive": "Expand TAM into APAC."
        })
        assert wf_res.status_code == 201
        wf_a_id = wf_res.json()["data"]["id"]

        # 8. Start Workflow Execution -> CEO Orchestrator -> Specialist Agents -> Tasks -> Report
        print(f"\n[8/15] Starting Workflow Execution ({wf_a_id})...")
        start_res = await client.post(f"{api_v1}/workflows/{wf_a_id}/start", headers=headers_a)
        assert start_res.status_code == 200
        assert start_res.json()["data"]["status"] == "COMPLETED"

        # 9. Verify Idempotency on Workflow Start
        print("\n[9/15] Testing Workflow Start Idempotency...")
        start_dup = await client.post(f"{api_v1}/workflows/{wf_a_id}/start", headers=headers_a)
        assert start_dup.status_code == 200
        assert start_dup.json()["data"]["status"] == "COMPLETED"

        # 10. Fetch Generated Executive Report
        print("\n[10/15] Fetching Executive Report...")
        rep_res = await client.get(f"{api_v1}/reports/workflow/{wf_a_id}", headers=headers_a)
        assert rep_res.status_code == 200
        report_a = rep_res.json()["data"]
        report_id = report_a["id"]
        assert report_a["overall_score"] > 0

        # 11. Fetch Dashboard Overview for Org A
        print("\n[11/15] Fetching Dashboard Overview for Org A...")
        dash_a = await client.get(f"{api_v1}/dashboard/overview", headers=headers_a)
        assert dash_a.status_code == 200
        data_a = dash_a.json()["data"]
        assert data_a["clients"]["total_clients"] == 1
        assert data_a["workflows"]["total_workflows"] == 1
        assert data_a["reports"]["total_reports"] == 1

        # 12. Multi-Tenant Security Isolation Check
        print("\n[12/15] SECURITY CHECK: Org B attempting to fetch Org A Report & Client...")
        cross_rep = await client.get(f"{api_v1}/reports/{report_id}", headers=headers_b)
        assert cross_rep.status_code == 404

        cross_client = await client.get(f"{api_v1}/clients/{client_a_id}", headers=headers_b)
        assert cross_client.status_code == 404

        dash_b = await client.get(f"{api_v1}/dashboard/overview", headers=headers_b)
        data_b = dash_b.json()["data"]
        assert data_b["clients"]["total_clients"] == 0

        # 13. Logout & JWT Blacklisting
        print("\n[13/15] Logging out Org A...")
        logout_res = await client.post(f"{api_v1}/auth/logout", headers=headers_a)
        assert logout_res.status_code == 200

        # 14. Verify Blacklisted JWT Rejection
        print("\n[14/15] SECURITY CHECK: Accessing /auth/me with Blacklisted JWT...")
        blacklisted_res = await client.get(f"{api_v1}/auth/me", headers=headers_a)
        assert blacklisted_res.status_code == 401

        print("\n[15/15] Full E2E Production Verification Complete!")

    print("\n=======================================================")
    print("ALL PRODUCTION INFRASTRUCTURE & E2E SUITE TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_full_production_e2e())
