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
        "access_token": generate_access_token(existing_user.id),
        "refresh_token": generate_refresh_token(existing_user.id),
    }

def generate_expired_token(key, id):
    return jwt.encode({
        "exp": datetime.now(tz=timezone.utc) - timedelta(days=30),
        "sub": str(id), 
    }, key, algorithm="HS256")

@pytest.fixture
def expired_refresh_token(existing_user: User):
    return generate_expired_token(REFRESH_TOKEN_SECRET, 
                                  existing_user.id)

@pytest.fixture
def valid_refresh_token():
    return generate_refresh_token(1) 


@pytest.fixture
def alt_valid_access_token():
    """ Valid access token, but not related to any user """
    return generate_access_token(-1)


@pytest.fixture
def access_token_of_user_with_tasks(existing_user_tokens, app):
    """ 
    Extends user creation fixture, creating 
    two tasks for exibition 
    """
    access_token: str =  existing_user_tokens["access_token"]
    from app.services.task_service import create_task
    from app.services.auth_service import user_from_access_token
    user_id = int(user_from_access_token(access_token)["sub"])
    
    with app.app_context(): 
        create_task(user_id,  {
            "title": "Buy groceries", 
            "description": "Buy milk, eggs, bread"
        })
    
        create_task(user_id,  {
            "title": "Pay bills",
            "description": "Pay electricity and water bills"    
        })

        return access_token
