def test_api_index(client):
    resp = client.get("/api/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"].startswith("A-Impact Licensing Assistant API")


def test_api_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
