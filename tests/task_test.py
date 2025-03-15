from flask import request
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from werkzeug.utils import header_property

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
    assert response.get_json()["message"] == "Missing information"


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

    # Task is not found
    assert response.status_code == 404
    assert response.get_json()["message"] == "Task not found"


def test_update_task_not_owned(client: FlaskClient, 
                               existing_user_tokens: dict, 
                               alt_valid_access_token: str):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    # Creates a valid task
    task_id: int = client.post("/todos", 
                               json=task, headers=headers).get_json()["id"]
    
    # "User" with different id from the owner
    headers["Authorization"] = f"Bearer {alt_valid_access_token}"

    response: TestResponse = client.put(f"/todos/{task_id}", 
                                        json=task_2, headers=headers)
    
    # User does not have permission (didn't create the resource)
    assert response.status_code == 403 # Forbidden
    assert response.get_json()["message"] == "Forbidden"


def test_update_task_with_success(client: FlaskClient, existing_user_tokens: dict):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    # Creates a valid task
    task_id: int = client.post("/todos", 
                               json=task, headers=headers).get_json()["id"]
    response: TestResponse = client.put(f"/todos/{task_id}", 
                                        json=task_2, headers=headers)

    # Task is found and update is done
    assert response.status_code == 200
    assert response.get_json() == {"id": task_id, **task_2}


def test_delete_non_existent_task(client: FlaskClient, existing_user_tokens: dict):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    # Try do delete a task that does not exist
    response: TestResponse = client.delete("/todos/0", 
                                           headers=headers)
    
    # Task not found
    assert response.status_code == 404 
    assert response.get_json()["message"] == "Task not found"


def test_delete_not_owned_task(client: FlaskClient, existing_user_tokens: dict, alt_valid_access_token: str):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    task_id = client.post("/todos", json=task, headers=headers).get_json()["id"]

    # Try do delete a task without permission
    headers["Authorization"] = f"Bearer {alt_valid_access_token}"
    response: TestResponse = client.delete(f"/todos/{task_id}", 
                                           headers=headers)
    
    # Forbidden
    assert response.status_code == 403
    assert response.get_json()["message"] == "Forbidden"


def test_delete_task_with_success(client: FlaskClient, existing_user_tokens: dict):
    headers = {"Authorization": f"Bearer {existing_user_tokens['access_token']}"}
    task_id = client.post("/todos", json=task, headers=headers).get_json()["id"]

    # Deleting the task 
    response: TestResponse = client.delete(f"/todos/{task_id}", 
                                           headers=headers)
    
    # Success
    assert response.status_code == 204

    # Task does not exist
    assert client.delete(f"/todos/{task_id}", headers=headers).status_code == 404


def test_get_todos_without_authentication(client: FlaskClient):
    response: TestResponse = client.get(f"/todos")
    
    # Unauthorized (doesn't have auth header)
    assert response.status_code == 401
    assert response.get_json()["message"] == "Unauthorized"


def test_get_todos_with_invalid_args(client: FlaskClient, 
                                     access_token_of_user_with_tasks: str):
    headers = {"Authorization": f"Bearer {access_token_of_user_with_tasks}"}
    response: TestResponse = client.get(f"/todos?page=-1&limit=0&invalid=invalid",
                                        headers=headers)
    
    # Bad request (invalid arguments)
    assert response.status_code == 400
    assert response.get_json()["message"] == "Invalid request"
    print(response.get_json())
    assert response.get_json()["errors"] == [
        "Invalid value for page '-1' (should be higher than 0)",
        "Invalid value for limit '0' (should be higher than 0)",
        "Unexpected parameters: invalid"
    ]


def test_get_todos_with_valid_request(client: FlaskClient, 
                                     access_token_of_user_with_tasks: str):
    headers = {"Authorization": f"Bearer {access_token_of_user_with_tasks}"}
    response: TestResponse = client.get(f"/todos?page=1&limit=10",
                                        headers=headers)

    # Successfull request
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 2
    assert response.get_json()["page"] == 1
    assert response.get_json()["limit"] == 10
    assert response.get_json()["total"] == 2
