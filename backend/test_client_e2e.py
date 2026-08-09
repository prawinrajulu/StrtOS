import asyncio
import uuid
import httpx

async def run_client_e2e_verification():
    base_auth_url = "http://localhost:8000/api/v1/auth"
    base_client_url = "http://localhost:8000/api/v1/clients"
    base_ceo_url = "http://localhost:8000/api/v1/ceo"

    uid_a = str(uuid.uuid4())[:8]
    email_a = f"admin-orgA-{uid_a}@acme.com"
    org_a = f"Org-A-{uid_a}"

    uid_b = str(uuid.uuid4())[:8]
    email_b = f"admin-orgB-{uid_b}@globex.com"
    org_b = f"Org-B-{uid_b}"

    password = "Password123!"

    print("\n=======================================================")
    print("STARTING CLIENT MANAGEMENT & TENANT ISOLATION E2E TEST")
    print("=======================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register Org A & Login
        print(f"\n[1/7] Registering Org A ({email_a})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_a, "full_name": "Admin Org A", "email": email_a, "password": password
        })
        login_a = await client.post(f"{base_auth_url}/login", json={"email": email_a, "password": password})
        token_a = login_a.json()["data"]["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register Org B & Login
        print(f"[2/7] Registering Org B ({email_b})...")
        await client.post(f"{base_auth_url}/register", json={
            "organization_name": org_b, "full_name": "Admin Org B", "email": email_b, "password": password
        })
        login_b = await client.post(f"{base_auth_url}/login", json={"email": email_b, "password": password})
        token_b = login_b.json()["data"]["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Org A creates a Client
        print(f"\n[3/7] Org A creating client 'Apex Health Solutions'...")
        create_res_a = await client.post(f"{base_client_url}", headers=headers_a, json={
            "name": "Apex Health Solutions",
            "industry": "HealthTech",
            "website_url": "https://apexhealth.io",
            "business_goal": "Scale telemedicine user acquisition by 45% in Q4.",
            "monthly_budget": 25000,
            "currency": "USD"
        })
        print("Create Status:", create_res_a.status_code)
        client_a_data = create_res_a.json()["data"]
        client_a_id = client_a_data["id"]
        print("Created Client ID:", client_a_id)

        # 4. Org A lists its Clients
        print(f"\n[4/7] Org A listing its clients...")
        list_res_a = await client.get(f"{base_client_url}", headers=headers_a)
        print("Org A Client Count:", len(list_res_a.json()["data"]["clients"]))
        assert len(list_res_a.json()["data"]["clients"]) >= 1

        # 5. CROSS-TENANT SECURITY CHECK: Org B attempts to access Org A's client
        print(f"\n[5/7] SECURITY CHECK: Org B attempting GET /clients/{client_a_id}...")
        cross_get = await client.get(f"{base_client_url}/{client_a_id}", headers=headers_b)
        print("Cross-tenant GET Status:", cross_get.status_code)
        assert cross_get.status_code == 404, "SECURITY VIOLATION: Cross-tenant GET succeeded!"

        print(f"SECURITY CHECK: Org B attempting PATCH /clients/{client_a_id}...")
        cross_patch = await client.patch(f"{base_client_url}/{client_a_id}", headers=headers_b, json={"name": "Hacked"})
        print("Cross-tenant PATCH Status:", cross_patch.status_code)
        assert cross_patch.status_code == 404, "SECURITY VIOLATION: Cross-tenant PATCH succeeded!"

        print(f"SECURITY CHECK: Org B attempting DELETE /clients/{client_a_id}...")
        cross_delete = await client.delete(f"{base_client_url}/{client_a_id}", headers=headers_b)
        print("Cross-tenant DELETE Status:", cross_delete.status_code)
        assert cross_delete.status_code == 404, "SECURITY VIOLATION: Cross-tenant DELETE succeeded!"

        # 6. CEO AGENT INTEGRATION: Initiate directive with real Client ID
        print(f"\n[6/7] Submitting CEO Directive with real Client ID ({client_a_id})...")
        ceo_res = await client.post(f"{base_ceo_url}/directive", headers=headers_a, json={
            "client_id": client_a_id,
            "directive": "Execute growth strategy for digital health expansion."
        })
        print("CEO Directive Status:", ceo_res.status_code)
        print("CEO Response:", ceo_res.json())
        assert ceo_res.status_code == 200
        assert ceo_res.json()["data"]["client_name"] == "Apex Health Solutions"

        # 7. Soft-delete / Archive Client as Org A
        print(f"\n[7/7] Org A archiving client ({client_a_id})...")
        archive_res = await client.delete(f"{base_client_url}/{client_a_id}", headers=headers_a)
        print("Archive Status:", archive_res.status_code)
        assert archive_res.json()["data"]["status"] == "ARCHIVED"

    print("\n=======================================================")
    print("ALL CLIENT MANAGEMENT & CROSS-TENANT SECURITY TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_client_e2e_verification())
