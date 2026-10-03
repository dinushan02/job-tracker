def register(c, email="a@example.com", password="password123"):
    return c.post("/auth/register", json={"email": email, "password": password})


def login(c, email="a@example.com", password="password123"):
    return c.post("/auth/login", data={"username": email, "password": password})


def bearer(c, email):
    token = login(c, email).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(anon_client):
    assert register(anon_client).status_code == 201
    r = login(anon_client)
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_duplicate_email_rejected(anon_client):
    register(anon_client)
    assert register(anon_client).status_code == 409


def test_wrong_password_rejected(anon_client):
    register(anon_client)
    assert login(anon_client, password="wrongpass1").status_code == 401


def test_applications_require_token(anon_client):
    assert anon_client.get("/applications").status_code == 401


def test_me_returns_current_user(anon_client):
    register(anon_client)
    r = anon_client.get("/auth/me", headers=bearer(anon_client, "a@example.com"))
    assert r.status_code == 200
    assert r.json()["email"] == "a@example.com"


def test_users_only_see_their_own_applications(anon_client):
    register(anon_client, "a@example.com")
    register(anon_client, "b@example.com")
    ha = bearer(anon_client, "a@example.com")
    hb = bearer(anon_client, "b@example.com")

    created = anon_client.post(
        "/applications", json={"company": "Acme", "role": "Dev"}, headers=ha
    )
    app_id = created.json()["id"]

    assert anon_client.get("/applications", headers=hb).json() == []
    assert anon_client.get(f"/applications/{app_id}", headers=hb).status_code == 404
    assert anon_client.delete(f"/applications/{app_id}", headers=hb).status_code == 404
    assert len(anon_client.get("/applications", headers=ha).json()) == 1