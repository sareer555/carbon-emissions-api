import pytest


def test_scope2_us_camx(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 12000, "region": "US-CAMX"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["emissions_kg_co2e"] == pytest.approx(12000 * 0.1981, rel=1e-6)
    assert "eGRID" in body["factor_source"]


def test_scope2_uk(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 1000, "region": "UK"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["emissions_kg_co2e"] == pytest.approx(1000 * 0.177, rel=1e-6)
    assert "DEFRA" in body["factor_source"] or "DESNZ" in body["factor_source"]


def test_scope2_unknown_region_rejected(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 1000, "region": "MARS-1"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_REGION"
