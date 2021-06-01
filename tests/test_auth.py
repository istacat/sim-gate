from typing import Generator
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_session, create_db, drop_db
from tests.utils.test_db import override_get_db, test_engine, TestingSessionLocal


app.dependency_overrides[get_session] = override_get_db


@pytest.fixture(scope="session")
def db() -> Generator:
    drop_db(test_engine)
    create_db(test_engine)

    yield TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


def test_auth(client, db):
    data = {
        "username": "Max",
        "password": "secret"
    }
    response = client.post("/auth/sign_up", json=data)
    assert response
    assert response.status_code == 200
    assert b"access_token" in response.content
    response = client.post("/auth/sign_in", data=data)
    assert response
    assert response.status_code == 200
    assert b"access_token" in response.content
    token = json.loads(response.content)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/user", headers=headers)
    assert response
    assert response.status_code == 200
    user = json.loads(response.content)["username"]
    assert user == data['username']
