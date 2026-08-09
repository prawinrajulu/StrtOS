import asyncio
import uuid
import httpx

async def run_dashboard_e2e_verification():
    base_auth_url = "http://localhost:8000/api/v1/auth"
    base_client_url = "http://localhost:8000/api/v1/clients"
    base_wf_url = "http://localhost:8000/api/v1/workflows"
    base_dash_url = "http://localhost:8000/api/v1/dashboard"

    uid_a = str(uuid.uuid4())[:8]
    email_a = f"dash-admin-orgA-{uid_a}@acme.com"
    org_a = f"Dash-Org-A-{uid_a}"

    uid_b = str(uuid.uuid4())[:8]
    email_b = f"dash-admin-orgB-{uid_b}@globex.com"
    org_b = f"Dash-Org-B-{uid_b}"

    password = "Password123!"

    print("\n=======================================================")
    print("STARTING EXECUTIVE DASHBOARD & MULTI-TENANT ANALYTICS E2E TEST")
    print("=======================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register Org A & Login
        print(f"\n[1/12] Registering Org A ({email_a})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_a, "full_name": "Admin Org A", "email": email_a, "password": password
        })
        login_a = await client.post(f"{base_auth_url}/login", json={"email": email_a, "password": password})
        token_a = login_a.json()["data"]["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register Org B & Login
        print(f"[2/12] Registering Org B ({email_b})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_b, "full_name": "Admin Org B", "email": email_b, "password": password
        })
        login_b = await client.post(f"{base_auth_url}/login", json={"email": email_b, "password": password})
        token_b = login_b.json()["data"]["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Verify Empty Org A Dashboard Metrics
        print(f"\n[3/12] Fetching initial Dashboard Overview for Org A...")
        init_res_a = await client.get(f"{base_dash_url}/overview", headers=headers_a)
        init_data_a = init_res_a.json()["data"]
        print("Initial Org A Clients:", init_data_a["clients"]["total_clients"])
        print("Initial Org A Workflows:", init_data_a["workflows"]["total_workflows"])
        assert init_res_a.status_code == 200
        assert init_data_a["clients"]["total_clients"] == 0

        # 4. Org A creates Client & Workflow
        print(f"\n[4/12] Org A creating Client & Executing Workflow...")
        cr = await client.post(f"{base_client_url}", headers=headers_a, json={
            "name": "OmniHealth", "industry": "HealthTech", "website_url": "https://omnihealth.io"
        })
        client_a_id = cr.json()["data"]["id"]

        wr = await client.post(f"{base_wf_url}", headers=headers_a, json={
            "client_id": client_a_id, "title": "OmniHealth Q4 Strategy"
        })
        wf_a_id = wr.json()["data"]["id"]

        await client.post(f"{base_wf_url}/{wf_a_id}/start", headers=headers_a)

        # 5. Verify Populated Dashboard Overview for Org A
        print(f"\n[5/12] Fetching updated Dashboard Overview for Org A...")
        updated_res_a = await client.get(f"{base_dash_url}/overview", headers=headers_a)
        data_a = updated_res_a.json()["data"]
        print("Updated Org A Total Clients:", data_a["clients"]["total_clients"])
        print("Updated Org A Total Workflows:", data_a["workflows"]["total_workflows"])
        print("Updated Org A Total Reports:", data_a["reports"]["total_reports"])
        print("Updated Org A Agent Performance Count:", len(data_a["agent_performance"]))
        assert data_a["clients"]["total_clients"] == 1
        assert data_a["workflows"]["total_workflows"] == 1
        assert data_a["reports"]["total_reports"] == 1
        assert len(data_a["agent_performance"]) >= 4

        # 6. Verify Sub-KPI Endpoints for Org A
        print(f"\n[6/12] Testing GET /dashboard/kpis...")
        kpis_res = await client.get(f"{base_dash_url}/kpis", headers=headers_a)
        assert kpis_res.status_code == 200

        print(f"\n[7/12] Testing GET /dashboard/workflows...")
        wf_kpi_res = await client.get(f"{base_dash_url}/workflows", headers=headers_a)
        assert wf_kpi_res.status_code == 200
        assert wf_kpi_res.json()["data"]["completed_workflows"] == 1

        print(f"\n[8/12] Testing GET /dashboard/agents...")
        agents_res = await client.get(f"{base_dash_url}/agents", headers=headers_a)
        assert agents_res.status_code == 200

        print(f"\n[9/12] Testing GET /dashboard/trends...")
        trends_res = await client.get(f"{base_dash_url}/trends?days=7", headers=headers_a)
        assert trends_res.status_code == 200
        assert len(trends_res.json()["data"]) == 7

        print(f"\n[10/12] Testing GET /dashboard/insights...")
        insights_res = await client.get(f"{base_dash_url}/insights", headers=headers_a)
        assert insights_res.status_code == 200
        print("Generated Insights:", insights_res.json()["data"])

        # 11. MULTI-TENANT SECURITY CHECK: Org B Dashboard MUST NOT expose Org A Data
        print(f"\n[11/12] SECURITY CHECK: Fetching Dashboard Overview for Org B...")
        data_b_res = await client.get(f"{base_dash_url}/overview", headers=headers_b)
        data_b = data_b_res.json()["data"]
        print("Org B Total Clients (Must be 0):", data_b["clients"]["total_clients"])
        print("Org B Total Workflows (Must be 0):", data_b["workflows"]["total_workflows"])
        assert data_b["clients"]["total_clients"] == 0
        assert data_b["workflows"]["total_workflows"] == 0
        assert len(data_b["agent_performance"]) == 0

        print(f"\n[12/12] Multi-Tenant Dashboard Isolation Verified Successfully!")

    print("\n=======================================================")
    print("ALL EXECUTIVE DASHBOARD & ANALYTICS TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_dashboard_e2e_verification())
