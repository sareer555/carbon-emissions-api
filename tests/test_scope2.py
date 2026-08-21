import pytest


def test_scope2_us_camx(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 12000, "region": "US-CAMX"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["emissions_kg_co2e"] == pytest.approx(12000 * 0.195, rel=1e-6)
    assert "eGRID" in body["factor_source"]


def test_scope2_uk(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 1000, "region": "UK"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["emissions_kg_co2e"] == pytest.approx(1000 * 0.13096, rel=1e-6)
    assert "DEFRA" in body["factor_source"] or "DESNZ" in body["factor_source"]


def test_scope2_uk_is_alias_for_latest_year(client, auth_headers):
    latest = client.post(
        "/v1/calculate/scope2", json={"kwh": 1000, "region": "UK"}, headers=auth_headers
    ).json()
    explicit_2026 = client.post(
        "/v1/calculate/scope2", json={"kwh": 1000, "region": "UK-2026"}, headers=auth_headers
    ).json()
    assert latest["emissions_kg_co2e"] == explicit_2026["emissions_kg_co2e"]


def test_scope2_uk_2025_historical_factor(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 1000, "region": "UK-2025"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["emissions_kg_co2e"] == pytest.approx(1000 * 0.177, rel=1e-6)
    assert "2025" in body["factor_source"]


def test_scope2_us_camx_is_alias_for_latest_egrid_year(client, auth_headers):
    latest = client.post(
        "/v1/calculate/scope2", json={"kwh": 1000, "region": "US-CAMX"}, headers=auth_headers
    ).json()
    explicit_2023 = client.post(
        "/v1/calculate/scope2", json={"kwh": 1000, "region": "US-CAMX-2023"}, headers=auth_headers
    ).json()
    assert latest["emissions_kg_co2e"] == explicit_2023["emissions_kg_co2e"]
    assert "2023" in explicit_2023["factor_source"]


def test_scope2_unknown_region_rejected(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope2",
        json={"kwh": 1000, "region": "MARS-1"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_REGION"
