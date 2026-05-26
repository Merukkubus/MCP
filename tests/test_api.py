import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_execute_success(client):
    response = client.post("/execute", json={
        "token": "123",
        "client_id": "test_client",
        "code": "print('Hello MCP')"
    })

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert "Hello MCP" in response.json["stdout"]


def test_execute_invalid_token(client):
    response = client.post("/execute", json={
        "token": "wrong",
        "client_id": "test_client",
        "code": "print('Hello')"
    })

    assert response.status_code == 401
    assert response.json["status"] == "unauthorized"


def test_execute_python_error(client):
    response = client.post("/execute", json={
        "token": "123",
        "client_id": "test_client",
        "code": "print(undefined_variable)"
    })

    assert response.status_code == 200
    assert response.json["status"] == "error"
    assert "NameError" in response.json["stderr"]


def test_execute_timeout(client):
    response = client.post("/execute", json={
        "token": "123",
        "client_id": "test_client",
        "code": "while True:\n    pass"
    })

    assert response.status_code == 200
    assert response.json["status"] == "timeout"


def test_forbidden_import(client):
    response = client.post("/execute", json={
        "token": "123",
        "client_id": "test_client",
        "code": "import os\nprint(os.getcwd())"
    })

    assert response.status_code == 403
    assert response.json["status"] == "forbidden"