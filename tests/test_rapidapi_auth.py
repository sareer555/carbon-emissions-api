"""Tests for the RapidAPI proxy-secret auth path (app/auth.py: authenticate())."""
from app.config import get_settings


def test_rapidapi_header_ignored_when_secret_not_configured(client, auth_headers):
    """With no RAPIDAPI_PROXY_SECRET set, the header is ignored and our own
    Bearer key still governs auth -- sending a bogus RapidAPI header must not
    grant access on its own."""
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers={"X-RapidAPI-Proxy-Secret": "whatever", "X-RapidAPI-User": "someuser"},
    )
    assert resp.status_code == 401


def test_rapidapi_valid_secret_authenticates_without_a_cek_key(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "rapidapi_proxy_secret", "test-rapidapi-secret")

    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers={
            "X-RapidAPI-Proxy-Secret": "test-rapidapi-secret",
            "X-RapidAPI-User": "someRapidApiUser",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["emissions_kg_co2e"] > 0


def test_rapidapi_wrong_secret_rejected(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "rapidapi_proxy_secret", "correct-secret")

    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers={"X-RapidAPI-Proxy-Secret": "wrong-secret", "X-RapidAPI-User": "someuser"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_rapidapi_caller_is_not_subject_to_local_monthly_quota(client, monkeypatch):
    """RapidAPI enforces the buyer's plan/quota on their own side; we don't
    double-enforce a local api_keys quota for this path since there's no
    local api_keys row for a RapidAPI caller."""
    from app import rate_limit

    monkeypatch.setattr(get_settings(), "rapidapi_proxy_secret", "test-rapidapi-secret")
    # Raise the burst limiter for this test so we're exercising the monthly
    # quota bypass, not the per-minute burst limiter (both apply to a
    # RapidAPI caller; only the monthly one is meant to be skipped).
    monkeypatch.setattr(rate_limit, "_limiter", rate_limit.InMemoryWindowLimiter(limit_per_minute=1000))
    headers = {
        "X-RapidAPI-Proxy-Secret": "test-rapidapi-secret",
        "X-RapidAPI-User": "heavy-user",
    }
    # Free plan quota is 100/month; a direct key would 429 on the 101st call.
    # A RapidAPI-authenticated caller should sail past that (still subject
    # to the burst rate limiter, not the monthly quota).
    for _ in range(105):
        resp = client.post(
            "/v1/calculate/scope1",
            json={"fuel_type": "natural_gas", "quantity": 1, "unit": "therms"},
            headers=headers,
        )
        assert resp.status_code == 200


def test_direct_key_still_works_when_rapidapi_secret_is_configured(client, auth_headers, monkeypatch):
    """The two auth paths coexist: configuring RAPIDAPI_PROXY_SECRET must not
    break direct cek_ customers who don't send the RapidAPI header at all."""
    monkeypatch.setattr(get_settings(), "rapidapi_proxy_secret", "test-rapidapi-secret")

    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
