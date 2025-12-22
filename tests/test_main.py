from fastapi.testclient import TestClient
from main import app

import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

client = TestClient(app)

def test_register_login_and_create_post():
    reg = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert reg.status_code == 200

    login = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    post = client.post("/posts", json={"content": "test post"}, headers=headers)
    assert post.status_code == 200
