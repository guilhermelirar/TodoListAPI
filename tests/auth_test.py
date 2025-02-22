from flask.testing import FlaskClient
from werkzeug.test import TestResponse

def test_register_with_missing_fields(client: FlaskClient):
    response: TestResponse = client.post('/register', json = {})

    assert response.status_code == 400
    response_json = response.get_json()

    assert 'message' in response_json
    assert response_json['message'] == 'Missing information'
