import pytest


def test_batch_mixed_scope1_and_scope2(client, auth_headers):
    payload = {
        "items": [
            {"scope": "scope1", "fuel_type": "natural_gas", "quantity": 500, "unit": "therms", "label": "jan-gas-bill"},
            {"scope": "scope2", "kwh": 12000, "region": "US-CAMX", "label": "jan-electric-bill"},
        ]
    }
    resp = client.post("/v1/calculate/batch", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    expected_total = 500 * 5.3115 + 12000 * 0.195
    assert body["total_emissions_kg_co2e"] == pytest.approx(expected_total, rel=1e-6)
    assert body["line_item_count"] == 2
    assert body["line_items"][0]["label"] == "jan-gas-bill"


def test_batch_missing_fields_for_scope1_rejected(client, auth_headers):
    payload = {"items": [{"scope": "scope1", "fuel_type": "diesel"}]}  # missing quantity/unit
    resp = client.post("/v1/calculate/batch", json=payload, headers=auth_headers)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_REQUEST"


def test_batch_empty_items_rejected(client, auth_headers):
    resp = client.post("/v1/calculate/batch", json={"items": []}, headers=auth_headers)
    assert resp.status_code == 422
