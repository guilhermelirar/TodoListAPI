import pytest
from app import create_app, db
from uuid import uuid4
from app.services import token_service
from app.models import User
import jwt
from datetime import datetime, timedelta, timezone

@pytest.fixture
def app():
    app = create_app(config_class="app.config.TestConfig")

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_email():
    """Unique email generator"""
    return f"test_{uuid4().hex[:8]}@email.com"

@pytest.fixture
def existing_user(app, test_email): 
    with app.app_context():
        new_user = User("John Doe", test_email, "password123")
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)
        
    return new_user 

@pytest.fixture
def existing_user_tokens(existing_user):
    """Access and Refresh tokens of valid user"""
    return {
        "access_token": token_service.generate_access_token(existing_user.id),
        "refresh_token": token_service.generate_refresh_token(existing_user.id)
    }

@pytest.fixture
def expired_token_generator():
    def _generate(key, user_id):
        return jwt.encode({
            "exp": datetime.now(tz=timezone.utc) - timedelta(days=30),
            "sub": str(user_id), 
            "iat": datetime.now(tz=timezone.utc) - timedelta(days=31),
        }, key, algorithm="HS256")
    return _generate

@pytest.fixture
def expired_refresh_token(existing_user, expired_token_generator):
    return expired_token_generator(token_service.REFRESH_TOKEN_SECRET, existing_user.id)

@pytest.fixture
def valid_refresh_token(existing_user):
    return token_service.generate_refresh_token(existing_user.id)

@pytest.fixture
def alt_valid_access_token():
     return token_service.generate_access_token(-1) 

@pytest.fixture
def user_id_from_token(existing_user_tokens):
    """Returns id in the token payload"""
    id = token_service.user_from_access_token(
        existing_user_tokens["access_token"]
    )

    return int(id)

@pytest.fixture
def tasks_creator(app):
    def _create_tasks(user_id, tasks_data=None):
        create_task = app.task_service.create_task
        
        default_tasks = [
            {"title": "Buy groceries", "description": "Buy milk, eggs, bread"},
            {"title": "Pay bills", "description": "Pay electricity and water bills"}
        ]
        
        tasks_data = tasks_data or default_tasks
        
        with app.app_context():
            for task_data in tasks_data:
                create_task(user_id, task_data)
    
    return _create_tasks

@pytest.fixture
def access_token_of_user_with_tasks(existing_user_tokens, user_id_from_token, tasks_creator):
    tasks_creator(user_id_from_token)
    return existing_user_tokens["access_token"]
