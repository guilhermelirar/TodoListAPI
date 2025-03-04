# Adding to PYTHONPATH
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import pytest
from app import create_app, db
from app.models import User
import jwt
from datetime import datetime
from app.services.auth_service import * 

@pytest.fixture
def app():
    app = create_app('app.config.TestConfig')
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def existing_user(app): 
    new_user: User
    with app.app_context():
        db.session.query(User).filter_by(email="existing@email.com").delete()
        db.session.commit()

        new_user = User("Existing", "existing@email.com", "password123")
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)
        
    return new_user

@pytest.fixture
def existing_user_tokens(existing_user: User):
    return {
        "access_token": generate_access_token(existing_user.id, existing_user.email),
        "refresh_token": generate_refresh_token(existing_user.id, existing_user.email),
    }

def generate_expired_token(key, id, email):
    return jwt.encode({
        "exp": datetime.now(tz=timezone.utc) - timedelta(days=30),
        "id": id, 
        "email": email
    }, key, algorithm="HS256")

@pytest.fixture
def expired_refresh_token(existing_user: User):
    return generate_expired_token(REFRESH_TOKEN_SECRET, 
                                  existing_user.id, 
                                  existing_user.email)

@pytest.fixture
def valid_refresh_token():
    return jwt.encode({
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=30),
        "id": 1, 
        "email": "auser@email.com"
    }, REFRESH_TOKEN_SECRET, algorithm="HS256")


@pytest.fixture
def alt_valid_access_token():
    """ Valid access token, but not related to any user """
    return generate_access_token(-1, "email@email.com")
