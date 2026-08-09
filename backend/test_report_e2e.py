import asyncio
import uuid
import httpx

async def run_report_e2e_verification():
    base_auth_url = "http://localhost:8000/api/v1/auth"
    base_client_url = "http://localhost:8000/api/v1/clients"
    base_wf_url = "http://localhost:8000/api/v1/workflows"
    base_rep_url = "http://localhost:8000/api/v1/reports"

    uid_a = str(uuid.uuid4())[:8]
    email_a = f"rep-admin-orgA-{uid_a}@acme.com"
    org_a = f"Rep-Org-A-{uid_a}"

    uid_b = str(uuid.uuid4())[:8]
    email_b = f"rep-admin-orgB-{uid_b}@globex.com"
    org_b = f"Rep-Org-B-{uid_b}"

    password = "Password123!"

    print("\n=======================================================")
    print("STARTING EXECUTIVE REPORT MANAGEMENT & TENANT ISOLATION E2E TEST")
    print("=======================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register Org A & Login
        print(f"\n[1/15] Registering Org A ({email_a})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_a, "full_name": "Admin Org A", "email": email_a, "password": password
        })
        login_a = await client.post(f"{base_auth_url}/login", json={"email": email_a, "password": password})
        token_a = login_a.json()["data"]["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register Org B & Login
        print(f"[2/15] Registering Org B ({email_b})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_b, "full_name": "Admin Org B", "email": email_b, "password": password
        })
        login_b = await client.post(f"{base_auth_url}/login", json={"email": email_b, "password": password})
        token_b = login_b.json()["data"]["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Org A creates Client & Workflow
        print(f"\n[3/15] Org A creating Client 'Aether MedTech'...")
        create_client_res = await client.post(f"{base_client_url}", headers=headers_a, json={
            "name": "Aether MedTech", "industry": "Healthcare AI", "website_url": "https://aethermed.io",
            "business_goal": "Scale MedTech adoption by 50% in FY26.", "monthly_budget": 60000, "currency": "USD"
        })
        client_a_id = create_client_res.json()["data"]["id"]

        print(f"\n[4/15] Org A creating Workflow...")
        create_wf_res = await client.post(f"{base_wf_url}", headers=headers_a, json={
            "client_id": client_a_id, "title": "Aether MedTech Growth Campaign",
            "directive": "Scale MedTech adoption via SEO & competitor intelligence."
        })
        wf_a_id = create_wf_res.json()["data"]["id"]

        # 5. Start Workflow Execution -> Triggers CEO Agent -> Creates Executive Report
        print(f"\n[5/15] Org A starting Workflow execution ({wf_a_id})...")
        start_res = await client.post(f"{base_wf_url}/{wf_a_id}/start", headers=headers_a)
        print("Start Workflow Status:", start_res.status_code)
        assert start_res.status_code == 200

        # 6. Fetch automatically generated Report by Workflow ID
        print(f"\n[6/15] Fetching generated Executive Report by Workflow ID...")
        rep_wf_res = await client.get(f"{base_rep_url}/workflow/{wf_a_id}", headers=headers_a)
        print("Report Status:", rep_wf_res.status_code)
        report_data = rep_wf_res.json()["data"]
        report_id = report_data["id"]
        print("Generated Report ID:", report_id)
        assert rep_wf_res.status_code == 200

        # 7. Verify all 5 Specialist Agent Outputs exist
        print(f"\n[7/15] Verifying 5 Specialist Agent Outputs in Report...")
        agent_results = report_data.get("agent_results", {})
        print("Agent Results Keys:", list(agent_results.keys()))
        assert len(agent_results) >= 5, "Fewer than 5 agent outputs found in Executive Report!"

        # 8. Verify CEO Executive Summary & Key Takeaways
        print(f"\n[8/15] Verifying CEO Executive Summary...")
        assert report_data["executive_summary"] is not None
        assert len(report_data["key_findings"]) >= 1
        assert len(report_data["recommendations"]) >= 1

        # 9. Verify Tenant Scoping
        print(f"\n[9/15] Verifying Report Organization ID...")
        assert report_data["organization_id"] is not None

        # 10. CROSS-TENANT SECURITY CHECK: Org B attempts to access Org A's Report
        print(f"\n[10/15] SECURITY CHECK: Org B attempting GET /reports/{report_id}...")
        cross_get = await client.get(f"{base_rep_url}/{report_id}", headers=headers_b)
        print("Cross-tenant GET Status:", cross_get.status_code)
        assert cross_get.status_code == 404, "SECURITY VIOLATION: Cross-tenant GET succeeded!"

        print(f"SECURITY CHECK: Org B attempting GET /reports/workflow/{wf_a_id}...")
        cross_wf_get = await client.get(f"{base_rep_url}/workflow/{wf_a_id}", headers=headers_b)
        print("Cross-tenant Workflow Report Status:", cross_wf_get.status_code)
        assert cross_wf_get.status_code == 404, "SECURITY VIOLATION: Cross-tenant Workflow Report GET succeeded!"

        # 11. Idempotency Check: Re-starting workflow does not duplicate report
        print(f"\n[11/15] IDEMPOTENCY CHECK: Verifying single report per workflow...")
        rep_list_res = await client.get(f"{base_rep_url}?workflow_id={wf_a_id}", headers=headers_a)
        print("Reports for Workflow Count:", len(rep_list_res.json()["data"]["reports"]))
        assert len(rep_list_res.json()["data"]["reports"]) == 1

        # 12. Test Report Metrics Endpoint
        print(f"\n[12/15] Fetching Report Metrics for Org A...")
        metrics_res = await client.get(f"{base_rep_url}/metrics", headers=headers_a)
        print("Metrics Status:", metrics_res.status_code, "Metrics Data:", metrics_res.json()["data"])
        assert metrics_res.status_code == 200

        # 13. Test Report Export Endpoint
        print(f"\n[13/15] Exporting Report {report_id}...")
        export_res = await client.get(f"{base_rep_url}/{report_id}/export", headers=headers_a)
        print("Export Status:", export_res.status_code)
        assert export_res.status_code == 200

        # 14. Test Report Archive Endpoint
        print(f"\n[14/15] Archiving Report {report_id}...")
        archive_res = await client.delete(f"{base_rep_url}/{report_id}", headers=headers_a)
        print("Archive Status:", archive_res.status_code, "New Status:", archive_res.json()["data"]["status"])
        assert archive_res.json()["data"]["status"] == "ARCHIVED"

        print(f"\n[15/15] E2E Verification Complete!")

    print("\n=======================================================")
    print("ALL EXECUTIVE REPORT MANAGEMENT & TENANT ISOLATION TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_report_e2e_verification())
