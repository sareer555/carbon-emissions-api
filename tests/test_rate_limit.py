from app import rate_limit


def test_burst_rate_limit_triggers(client, auth_headers, monkeypatch):
    # Tighten the limiter for this test so we don't need 60+ requests.
    tight_limiter = rate_limit.InMemoryWindowLimiter(limit_per_minute=3)
    monkeypatch.setattr(rate_limit, "_limiter", tight_limiter)

    statuses = []
    for _ in range(5):
        resp = client.get("/v1/factors", headers=auth_headers)
        statuses.append(resp.status_code)

    assert 429 in statuses
    idx = statuses.index(429)
    body = client.get("/v1/factors", headers=auth_headers).json()
    assert "error" in body
