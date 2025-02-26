from flask.testing import FlaskClient
from werkzeug.test import TestResponse

def test_register_with_missing_fields(client: FlaskClient):
    response: TestResponse = client.post('/register', json = {})

    assert response.status_code == 400
    response_json = response.get_json()

    assert 'message' in response_json
    assert response_json['message'] == 'Missing information'

def test_register_with_already_used_email(client: FlaskClient, existing_user):
    response: TestResponse = client.post('/register', json = {
        'name':'Name',
        'email':'existing@email.com',
        'password':'password123'
    })

    assert response.status_code == 400
    response_json = response.get_json()

    assert 'message' in response_json
    assert response_json['message'] == 'Email already in use'

def test_register_with_valid_email(client: FlaskClient):
    response: TestResponse = client.post('/register', json = {
        "name": "John Doe",
        "email": "john@doe.com",
        "password": "password"
    })

    assert response.status_code == 201
    response_json = response.get_json()

    assert 'access_token' in response_json
    assert 'refresh_token' in response_json

def test_invalid_refresh_token_rejected(client: FlaskClient):
    headers = {'Authorization': 'Bearer invalid_token'}
    response: TestResponse = client.post('/refresh', headers=headers)

    assert response.status_code == 401
    response_json = response.get_json()

    assert 'message' in response_json
    assert response_json['message'] == 'Unauthorized'
