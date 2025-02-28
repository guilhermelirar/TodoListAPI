from flask.testing import FlaskClient
import jwt
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
        'email':existing_user.email,
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


def test_expired_refresh_token_rejected(client: FlaskClient, expired_refresh_token: str):
    headers = {'Authorization': f'Bearer {expired_refresh_token}'}
    response: TestResponse = client.post('/refresh', headers=headers)

    assert response.status_code == 401
    response_json = response.get_json()

    assert 'message' in response_json
    assert response_json['message'] == 'Token expired, please login again.'


def test_valid_refresh_token_accepted(client: FlaskClient, valid_refresh_token: str):
    headers = {'Authorization': f'Bearer {valid_refresh_token}'}
    response: TestResponse = client.post('/refresh', headers=headers)

    assert response.status_code == 200
    response_json = response.get_json()

    assert 'token' in response_json


def test_login_with_missing_fields(client: FlaskClient):
    response: TestResponse = client.post('/login')

    assert response.status_code == 400
    response_json = response.get_json()

    assert 'message' in response_json
    assert response_json['message'] == 'Invalid request'

    response = client.post('/login', json={})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Missing information'


def test_login_with_nonexistant_user(client: FlaskClient):
    response: TestResponse = client.post('/login', json={
        "email": "inexist@email.com",
        "password": "password123"
    })

    assert response.status_code == 404
    assert response.get_json()['message'] == 'Invalid credentials'


def test_login_with_wrong_password(client: FlaskClient, existing_user):
    response: TestResponse = client.post('/login', json={
        "email": existing_user.email,
        "password": "wrongpassword"
    })

    assert response.status_code == 404
    assert response.get_json()['message'] == 'Invalid credentials'

def test_with_valid_credentials(client: FlaskClient, existing_user):
    response: TestResponse = client.post('/login', json={
        "email": existing_user.email,
        "password": "password123"
    })

    assert response.status_code == 200
    assert len(response.get_json()) == 2
