def make(client, **overrides):
    data = {"company": "Acme", "role": "Python Developer"}
    data.update(overrides)
    return client.post("/applications", json=data)


def test_create_application(client):
    r = make(client)
    assert r.status_code == 201
    body = r.json()
    assert body["company"] == "Acme"
    assert body["status"] == "applied"
    assert "id" in body


def test_create_requires_company(client):
    r = client.post("/applications", json={"role": "Dev"})
    assert r.status_code == 422


def test_list_and_filter_by_status(client):
    make(client)
    make(client, company="Globex", status="interview")
    assert len(client.get("/applications").json()) == 2
    r = client.get("/applications", params={"status": "interview"})
    assert [a["company"] for a in r.json()] == ["Globex"]


def test_search_by_company(client):
    make(client)
    make(client, company="Globex")
    r = client.get("/applications", params={"q": "glob"})
    assert len(r.json()) == 1


def test_update_application(client):
    app_id = make(client).json()["id"]
    r = client.put(f"/applications/{app_id}", json={"status": "offer"})
    assert r.status_code == 200
    assert r.json()["status"] == "offer"
    assert r.json()["company"] == "Acme"


def test_delete_application(client):
    app_id = make(client).json()["id"]
    assert client.delete(f"/applications/{app_id}").status_code == 204
    assert client.get(f"/applications/{app_id}").status_code == 404


def test_get_missing_returns_404(client):
    assert client.get("/applications/999").status_code == 404