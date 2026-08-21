def test_list_factors(client, auth_headers):
    resp = client.get("/v1/factors", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["scope1_fuels"]) == 4
    assert len(body["scope2_grids"]) >= 5
    keys = {f["key"] for f in body["scope1_fuels"]}
    assert {"natural_gas", "diesel", "gasoline", "propane"} <= keys
    assert "disclaimer" in body
