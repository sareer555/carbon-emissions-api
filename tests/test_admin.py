from app.config import get_settings


def test_admin_endpoint_disabled_when_no_token_configured(client):
    resp = client.post(
        "/v1/admin/keys",
        json={"plan": "free", "label": "should-fail"},
        headers={"Authorization": "Bearer anything"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_admin_endpoint_creates_key_and_it_works(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "admin_bootstrap_token", "test-admin-secret")

    resp = client.post(
        "/v1/admin/keys",
        json={"plan": "free", "label": "bootstrap-test"},
        headers={"Authorization": "Bearer test-admin-secret"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["api_key"].startswith("cek_")
    assert body["plan"] == "free"
    assert body["label"] == "bootstrap-test"

    # The freshly issued key should actually authenticate against the real API.
    calc_resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "therms"},
        headers={"Authorization": f"Bearer {body['api_key']}"},
    )
    assert calc_resp.status_code == 200


def test_admin_endpoint_rejects_wrong_token(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "admin_bootstrap_token", "correct-secret")

    resp = client.post(
        "/v1/admin/keys",
        json={"plan": "free"},
        headers={"Authorization": "Bearer wrong-secret"},
    )
    assert resp.status_code == 401
