from flask.testing import FlaskClient
from werkzeug.test import TestResponse

task = { "title": "Buy groceries", "description": "Buy milk, eggs, and bread" }
task_2 = { "title": "Buy groceries", "description": "Buy milk, eggs, bread and cheese" }

def test_create_task_requires_authorization(client: FlaskClient):
    response: TestResponse = client.post("/todos", json=task)

    assert response.status_code == 401
    assert response.get_json()["message"] == "Unauthorized"

def test_create_task_rejects_invalid_token(client: FlaskClient):
    response: TestResponse = client.post("/todos", json=task, 
                                         headers={"Authorization":"Bearer invalid"})

    assert response.status_code == 401
    assert response.get_json()["message"] == "Unauthorized"

def test_create_task_with_invalid_fields(client: FlaskClient, 
                                         existing_user_tokens: dict):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    response: TestResponse = client.post("/todos", json={}, headers=headers)

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing fields"

def test_create_task_with_success(client: FlaskClient, existing_user_tokens: dict):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    response: TestResponse = client.post("/todos", json=task, headers=headers)

    # To-do item created with success
    assert response.status_code == 201
    # Details of created item are present
    res_json = response.get_json()
    assert len(res_json) == 3 

def test_update_nonexistent_task(client: FlaskClient, existing_user_tokens: dict):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    response: TestResponse = client.put("/todos/0", json=task_2, headers=headers)

    # To-do item created with success
    assert response.status_code == 404
    # Details of created item are present
    assert response.get_json()["message"] == "Task not found"
 
