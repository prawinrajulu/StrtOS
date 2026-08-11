import uuid
from fastapi.testclient import TestClient
from app.main import app

def test_step_by_step():
    client = TestClient(app)

    base_auth_url = "/api/v1/auth"
    base_client_url = "/api/v1/clients"
    base_wf_url = "/api/v1/workflows"

    uid_a = str(uuid.uuid4())[:8]
    email_a = f"wf-admin-orgA-{uid_a}@acme.com"
    org_a = f"Wf-Org-A-{uid_a}"

    uid_b = str(uuid.uuid4())[:8]
    email_b = f"wf-admin-orgB-{uid_b}@globex.com"
    org_b = f"Wf-Org-B-{uid_b}"

    password = "Password123!"

    print("\n--- STEP 1 & 2: REGISTER & LOGIN ---")
    r1 = client.post(f"{base_auth_url}/register", json={"organization_name": org_a, "full_name": "Admin Org A", "email": email_a, "password": password})
    assert r1.status_code == 201
    r2 = client.post(f"{base_auth_url}/login", json={"email": email_a, "password": password})
    assert r2.status_code == 200
    token_a = r2.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    r3 = client.post(f"{base_auth_url}/register", json={"organization_name": org_b, "full_name": "Admin Org B", "email": email_b, "password": password})
    assert r3.status_code == 201
    r4 = client.post(f"{base_auth_url}/login", json={"email": email_b, "password": password})
    assert r4.status_code == 200
    token_b = r4.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("\n--- STEP 3: CREATE CLIENT ---")
    cr = client.post(f"{base_client_url}", headers=headers_a, json={
        "name": "Helios SaaS", "industry": "Cloud SaaS", "website_url": "https://helios.io",
        "business_goal": "Scale ARR from $2M to $5M in FY26.", "monthly_budget": 45000, "currency": "USD"
    })
    assert cr.status_code == 201
    client_a_id = cr.json()["data"]["id"]

    print("\n--- STEP 4: CREATE WORKFLOW ---")
    wr = client.post(f"{base_wf_url}", headers=headers_a, json={
        "client_id": client_a_id, "title": "Helios FY26 ARR Scale Campaign",
        "directive": "Scale ARR from $2M to $5M via enterprise SEO & competitor positioning."
    })
    assert wr.status_code == 201
    wf_a_id = wr.json()["data"]["id"]

    print("\n--- STEP 5: TENANT ISOLATION CHECK ---")
    cg = client.get(f"{base_wf_url}/{wf_a_id}", headers=headers_b)
    assert cg.status_code == 404
    cs = client.post(f"{base_wf_url}/{wf_a_id}/start", headers=headers_b)
    assert cs.status_code == 404

    print("\n--- STEP 6: START WORKFLOW EXECUTION ---")
    sr = client.post(f"{base_wf_url}/{wf_a_id}/start", headers=headers_a)
    assert sr.status_code == 200

    print("\n--- STEP 7: GET TASKS ---")
    tr = client.get(f"{base_wf_url}/{wf_a_id}/tasks", headers=headers_a)
    assert tr.status_code == 200
    assert len(tr.json()["data"]) >= 4

    print("\n--- STEP 8: GET EVENTS ---")
    er = client.get(f"{base_wf_url}/{wf_a_id}/events", headers=headers_a)
    assert er.status_code == 200
    assert len(er.json()["data"]) >= 1

    print("\nALL STEPS COMPLETED!")

if __name__ == "__main__":
    test_step_by_step()
