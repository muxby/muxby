def test_create_and_list_hospitals(client, auth_headers):
    r = client.post(
        "/api/hospitals",
        json={"name": "North General", "region": "North", "data_size": 500},
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "online"
    assert body["data_size"] == 500

    listing = client.get("/api/hospitals", headers=auth_headers).json()
    assert [h["name"] for h in listing] == ["North General"]


def test_duplicate_hospital_name_rejected(client, auth_headers):
    payload = {"name": "Twin", "region": "East", "data_size": 200}
    assert client.post("/api/hospitals", json=payload, headers=auth_headers).status_code == 201
    assert client.post("/api/hospitals", json=payload, headers=auth_headers).status_code == 409


def test_get_update_delete_hospital(client, auth_headers, hospital_id):
    detail = client.get(f"/api/hospitals/{hospital_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["metrics"] == []

    updated = client.patch(
        f"/api/hospitals/{hospital_id}",
        json={"region": "South", "status": "offline"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["region"] == "South"
    assert updated.json()["status"] == "offline"

    assert client.delete(f"/api/hospitals/{hospital_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/hospitals/{hospital_id}", headers=auth_headers).status_code == 404


def test_hospital_validation(client, auth_headers):
    r = client.post(
        "/api/hospitals",
        json={"name": "Tiny", "region": "West", "data_size": 5},  # below minimum
        headers=auth_headers,
    )
    assert r.status_code == 422
    r = client.patch("/api/hospitals/999", json={"region": "X"}, headers=auth_headers)
    assert r.status_code == 404


def test_rename_to_existing_name_conflicts(client, auth_headers):
    a = client.post("/api/hospitals", json={"name": "A", "region": "N", "data_size": 100}, headers=auth_headers).json()
    client.post("/api/hospitals", json={"name": "B", "region": "N", "data_size": 100}, headers=auth_headers)
    r = client.patch(f"/api/hospitals/{a['id']}", json={"name": "B"}, headers=auth_headers)
    assert r.status_code == 409
