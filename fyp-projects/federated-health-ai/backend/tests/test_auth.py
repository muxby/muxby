def test_register_login_me_flow(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "u@x.io", "password": "password1", "full_name": "User X"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "u@x.io"
    assert body["role"] == "admin"  # first user becomes admin
    assert "hashed_password" not in body

    token = client.post("/api/auth/login", data={"username": "u@x.io", "password": "password1"})
    assert token.status_code == 200
    access = token.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == "u@x.io"


def test_second_user_is_researcher(client):
    client.post("/api/auth/register", json={"email": "a@x.io", "password": "password1", "full_name": "A"})
    r = client.post("/api/auth/register", json={"email": "b@x.io", "password": "password1", "full_name": "B"})
    assert r.json()["role"] == "researcher"


def test_duplicate_email_rejected(client):
    payload = {"email": "dup@x.io", "password": "password1", "full_name": "Dup"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_short_password_rejected(client):
    r = client.post(
        "/api/auth/register", json={"email": "s@x.io", "password": "short", "full_name": "S"}
    )
    assert r.status_code == 422


def test_wrong_password_rejected(client):
    client.post("/api/auth/register", json={"email": "w@x.io", "password": "password1", "full_name": "W"})
    r = client.post("/api/auth/login", data={"username": "w@x.io", "password": "password2"})
    assert r.status_code == 401


def test_unknown_user_login_rejected(client):
    assert client.post("/api/auth/login", data={"username": "no@x.io", "password": "whatever1"}).status_code == 401


def test_protected_routes_require_token(client):
    assert client.get("/api/hospitals").status_code == 401
    assert client.get("/api/rounds").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer bogus"}).status_code == 401
