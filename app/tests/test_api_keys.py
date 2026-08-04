from httpx import AsyncClient


async def test_admin_api_key_lifecycle(
    client: AsyncClient, admin_headers: dict[str, str]
):
    """Tests the full API Key lifecycle: creation, usage, listing, and revocation."""

    # 1. Attempt key creation with invalid admin secret (Expect 403)
    bad_res = await client.post(
        "/api/v1/api-keys",
        json={"name": "LMS Backend", "app_name": "lms"},
        headers={"X-Secret": "invalid_secret"},
    )
    assert bad_res.status_code == 403

    # 2. Create API key with valid admin secret (Expect 201)
    res = await client.post(
        "/api/v1/api-keys",
        json={"name": "LMS Backend", "app_name": "lms"},
        headers=admin_headers,
    )
    assert res.status_code == 201
    data = res.json()
    assert "raw_key" in data
    assert data["key_prefix"] == "gw_live_"
    raw_key = data["raw_key"]
    key_id = data["id"]

    # 3. Access protected route with valid Bearer key (Expect 200)
    auth_headers = {"Authorization": f"Bearer {raw_key}"}
    models_res = await client.get("/api/v1/models", headers=auth_headers)
    assert models_res.status_code == 200

    # 4. List all generated keys (Expect 200)
    list_res = await client.get("/api/v1/api-keys", headers=admin_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Revoke API key (Expect 204)
    revoke_res = await client.delete(
        f"/api/v1/api-keys/{key_id}", headers=admin_headers
    )
    assert revoke_res.status_code == 204

    # 6. Access protected route with revoked key (Expect 401 Unauthorized)
    rejected_res = await client.get("/api/v1/models", headers=auth_headers)
    assert rejected_res.status_code == 401
