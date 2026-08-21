def test_missing_auth_header_rejected(client):
    resp = client.post("/v1/calculate/scope1", json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_invalid_key_rejected(client):
    headers = {"Authorization": "Bearer not_a_real_key"}
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers=headers,
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_valid_key_accepted(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers=auth_headers,
    )
    assert resp.status_code == 200


def test_monthly_quota_enforced(client, auth_headers, monkeypatch):
    from app import rate_limit

    # Free plan quota is 100 calls/month; raise the burst limit for this test
    # so we're exercising the monthly quota, not the per-minute burst limiter.
    monkeypatch.setattr(rate_limit, "_limiter", rate_limit.InMemoryWindowLimiter(limit_per_minute=1000))

    for _ in range(100):
        resp = client.post(
            "/v1/calculate/scope1",
            json={"fuel_type": "natural_gas", "quantity": 1, "unit": "therms"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 1, "unit": "therms"},
        headers=auth_headers,
    )
    assert resp.status_code == 429
    assert resp.json()["error"]["code"] == "MONTHLY_QUOTA_EXCEEDED"
