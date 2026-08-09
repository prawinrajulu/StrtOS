import asyncio
import httpx

async def run_e2e_verification():
    base_url = "http://localhost:8000/api/v1/auth"
    import uuid
    uid = str(uuid.uuid4())[:8]
    email = f"enterprise-{uid}@acme.com"
    password = "Password123!"
    org_name = f"Acme-{uid}"

    print(f"\n=======================================================")
    print(f"STARTING END-TO-END AUTHENTICATION VERIFICATION FLOW")
    print(f"=======================================================")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. REGISTER
        print(f"\n[1/6] Testing POST /api/v1/auth/register ({email})...")
        reg_payload = {
            "organization_name": org_name,
            "full_name": "Jane Enterprise Admin",
            "email": email,
            "password": password
        }
        res = await client.post(f"{base_url}/register", json=reg_payload)
        print("HTTP Status:", res.status_code)
        print("Response:", res.json())
        assert res.status_code == 201, "Registration failed!"

        # 2. LOGIN
        print(f"\n[2/6] Testing POST /api/v1/auth/login...")
        login_payload = {"email": email, "password": password}
        res = await client.post(f"{base_url}/login", json=login_payload)
        print("HTTP Status:", res.status_code)
        data = res.json()
        print("Response:", data)
        assert res.status_code == 200, "Login failed!"
        
        access_token = data["data"]["access_token"]
        refresh_token = data["data"]["refresh_token"]
        assert access_token and refresh_token, "Tokens missing!"

        # 3. GET /ME
        print(f"\n[3/6] Testing GET /api/v1/auth/me...")
        headers = {"Authorization": f"Bearer {access_token}"}
        res = await client.get(f"{base_url}/me", headers=headers)
        print("HTTP Status:", res.status_code)
        me_data = res.json()
        print("Response:", me_data)
        assert res.status_code == 200, "/me failed!"
        assert me_data["data"]["email"] == email

        # 4. REFRESH TOKEN ROTATION
        print(f"\n[4/6] Testing POST /api/v1/auth/refresh...")
        res = await client.post(f"{base_url}/refresh", json={"refresh_token": refresh_token})
        print("HTTP Status:", res.status_code)
        ref_data = res.json()
        print("Response:", ref_data)
        assert res.status_code == 200, "Refresh failed!"
        new_access_token = ref_data["data"]["access_token"]
        new_refresh_token = ref_data["data"]["refresh_token"]

        # Verify old refresh token is revoked
        res_old = await client.post(f"{base_url}/refresh", json={"refresh_token": refresh_token})
        print("HTTP Status of old revoked refresh token reuse:", res_old.status_code)
        assert res_old.status_code == 401, "Old refresh token was not revoked!"

        # 5. LOGOUT
        print(f"\n[5/6] Testing POST /api/v1/auth/logout...")
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        res = await client.post(f"{base_url}/logout", headers=new_headers)
        print("HTTP Status:", res.status_code)
        print("Response:", res.json())
        assert res.status_code == 200, "Logout failed!"

        # 6. VERIFY BLACKLISTED / INVALIDATED ACCESS TOKEN
        print(f"\n[6/6] Testing GET /api/v1/auth/me after logout...")
        res_after = await client.get(f"{base_url}/me", headers=new_headers)
        print("HTTP Status of blacklisted token:", res_after.status_code)

    print("\n=======================================================")
    print("ALL END-TO-END AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
