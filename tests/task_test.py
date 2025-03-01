from flask.testing import FlaskClient
from werkzeug.test import TestResponse

def test_create_task_requires_authorization(client: FlaskClient):
    response: TestResponse = client.post("/todos", json={
        "title": "Buy groceries",
        "description": "Buy milk, eggs, and bread"       
    })

    assert response.status_code == 401
    assert response.get_json()["message"] == "Unauthorized"

def test_create_task_rejects_invalid_token(client: FlaskClient):
    response: TestResponse = client.post("/todos", json={
        "title": "Buy groceries",
        "description": "Buy milk, eggs, and bread"       
    }, headers={"Authorization":"Bearer invalid"})

    assert response.status_code == 401
    assert response.get_json()["message"] == "Unauthorized"
