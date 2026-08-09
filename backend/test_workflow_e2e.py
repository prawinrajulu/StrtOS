import asyncio
import uuid
import httpx

async def run_workflow_e2e_verification():
    base_auth_url = "http://localhost:8000/api/v1/auth"
    base_client_url = "http://localhost:8000/api/v1/clients"
    base_wf_url = "http://localhost:8000/api/v1/workflows"

    uid_a = str(uuid.uuid4())[:8]
    email_a = f"wf-admin-orgA-{uid_a}@acme.com"
    org_a = f"Wf-Org-A-{uid_a}"

    uid_b = str(uuid.uuid4())[:8]
    email_b = f"wf-admin-orgB-{uid_b}@globex.com"
    org_b = f"Wf-Org-B-{uid_b}"

    password = "Password123!"

    print("\n=======================================================")
    print("STARTING WORKFLOW MANAGEMENT & TENANT ISOLATION E2E TEST")
    print("=======================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register Org A & Login
        print(f"\n[1/9] Registering Org A ({email_a})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_a, "full_name": "Admin Org A", "email": email_a, "password": password
        })
        login_a = await client.post(f"{base_auth_url}/login", json={"email": email_a, "password": password})
        token_a = login_a.json()["data"]["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register Org B & Login
        print(f"[2/9] Registering Org B ({email_b})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_b, "full_name": "Admin Org B", "email": email_b, "password": password
        })
        login_b = await client.post(f"{base_auth_url}/login", json={"email": email_b, "password": password})
        token_b = login_b.json()["data"]["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Org A creates a Client
        print(f"\n[3/9] Org A creating Client 'Helios SaaS'...")
        create_client_res = await client.post(f"{base_client_url}", headers=headers_a, json={
            "name": "Helios SaaS",
            "industry": "Cloud SaaS",
            "website_url": "https://helios.io",
            "business_goal": "Scale ARR from $2M to $5M in FY26.",
            "monthly_budget": 45000,
            "currency": "USD"
        })
        client_a_id = create_client_res.json()["data"]["id"]
        print("Created Client ID:", client_a_id)

        # 4. Org A creates a Workflow
        print(f"\n[4/9] Org A creating Workflow for Client 'Helios SaaS'...")
        create_wf_res = await client.post(f"{base_wf_url}", headers=headers_a, json={
            "client_id": client_a_id,
            "title": "Helios FY26 ARR Scale Campaign",
            "directive": "Scale ARR from $2M to $5M via enterprise SEO & competitor positioning."
        })
        print("Create Workflow Status:", create_wf_res.status_code)
        wf_a_data = create_wf_res.json()["data"]
        wf_a_id = wf_a_data["id"]
        print("Created Workflow ID:", wf_a_id)

        # 5. CROSS-TENANT SECURITY CHECK: Org B attempts to access Org A's Workflow
        print(f"\n[5/9] SECURITY CHECK: Org B attempting GET /workflows/{wf_a_id}...")
        cross_get = await client.get(f"{base_wf_url}/{wf_a_id}", headers=headers_b)
        print("Cross-tenant GET Status:", cross_get.status_code)
        assert cross_get.status_code == 404, "SECURITY VIOLATION: Cross-tenant GET succeeded!"

        print(f"SECURITY CHECK: Org B attempting POST /workflows/{wf_a_id}/start...")
        cross_start = await client.post(f"{base_wf_url}/{wf_a_id}/start", headers=headers_b)
        print("Cross-tenant START Status:", cross_start.status_code)
        assert cross_start.status_code == 404, "SECURITY VIOLATION: Cross-tenant START succeeded!"

        # 6. START WORKFLOW Execution as Org A
        print(f"\n[6/9] Org A starting Workflow execution ({wf_a_id})...")
        start_res = await client.post(f"{base_wf_url}/{wf_a_id}/start", headers=headers_a)
        print("Start Workflow Status:", start_res.status_code)
        start_data = start_res.json()["data"]
        print("Workflow Status After Execution:", start_data["status"])
        assert start_res.status_code == 200
        assert start_data["status"] == "COMPLETED"
        assert start_data["progress"] == 100

        # 7. Fetch Persisted Tasks for Workflow
        print(f"\n[7/9] Fetching persisted tasks for Workflow ({wf_a_id})...")
        tasks_res = await client.get(f"{base_wf_url}/{wf_a_id}/tasks", headers=headers_a)
        tasks = tasks_res.json()["data"]
        print(f"Retrieved {len(tasks)} persisted tasks:")
        for t in tasks:
            print(f" - [{t['status']}] {t['agent_name']}: {t['title']}")
        assert len(tasks) >= 5

        # 8. Fetch Persisted Events for Workflow
        print(f"\n[8/9] Fetching audit events for Workflow ({wf_a_id})...")
        events_res = await client.get(f"{base_wf_url}/{wf_a_id}/events", headers=headers_a)
        events = events_res.json()["data"]
        print(f"Retrieved {len(events)} audit events:")
        for e in events:
            print(f" - {e['event_type']} @ {e['created_at']}")
        assert len(events) >= 2

        # 9. Verify Executive Report Endpoint
        print(f"\n[9/9] Fetching executive report for completed workflow...")
        rep_res = await client.get(f"http://localhost:8000/api/v1/ceo/report/{wf_a_id}", headers=headers_a)
        print("Report Status:", rep_res.status_code)

    print("\n=======================================================")
    print("ALL WORKFLOW MANAGEMENT & TENANT ISOLATION TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_workflow_e2e_verification())
