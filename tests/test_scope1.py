import pytest


def test_scope1_natural_gas(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 500, "unit": "therms"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["emissions_kg_co2e"] == pytest.approx(500 * 5.311, rel=1e-6)
    assert body["factor_source"].startswith("EPA")
    assert "estimate" in body["disclaimer"].lower()


def test_scope1_diesel_gallons(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "diesel", "quantity": 100, "unit": "gallons"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["emissions_kg_co2e"] == pytest.approx(100 * 10.21, rel=1e-6)


def test_scope1_diesel_liters_converted(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "diesel", "quantity": 378.541, "unit": "liters"},  # ~100 gallons
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["emissions_kg_co2e"] == pytest.approx(100 * 10.21, rel=1e-3)


def test_scope1_invalid_fuel_type_rejected_by_schema(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "coal", "quantity": 10, "unit": "kg"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_scope1_invalid_unit_rejected(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": 10, "unit": "kg"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_UNIT"


def test_scope1_negative_quantity_rejected(client, auth_headers):
    resp = client.post(
        "/v1/calculate/scope1",
        json={"fuel_type": "natural_gas", "quantity": -5, "unit": "therms"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
