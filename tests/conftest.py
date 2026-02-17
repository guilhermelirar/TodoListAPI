import pytest
from app import create_app, db
from uuid import uuid4
from app.models import User
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app


# ───────────────────────────────
# APP / CLIENT
# ───────────────────────────────

@pytest.fixture
def app():
    app = create_app(config_class="app.config.TestConfig")

    with app.app_context():
        db.create_all()
        yield app  # yield dentro do contexto

    # teardown
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    yield app.test_client()


# ───────────────────────────────
# SERVICES
# ───────────────────────────────

@pytest.fixture
def token_service(app):
    with app.app_context():
        yield current_app.token_service


@pytest.fixture
def task_service(app):
    with app.app_context():
        yield current_app.task_service


# ───────────────────────────────
# USERS
# ───────────────────────────────

@pytest.fixture
def test_email():
    yield f"test_{uuid4().hex[:8]}@email.com"


@pytest.fixture
def existing_user(app, test_email):
    with app.app_context():
        user = User("John Doe", test_email, "password123")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        yield user


# ───────────────────────────────
# TOKENS
# ───────────────────────────────

@pytest.fixture
def existing_user_tokens(existing_user, token_service):
    yield {
        "access_token": token_service.new_access_token(existing_user.id),
        "refresh_token": token_service.new_refresh_token(existing_user.id),
    }


@pytest.fixture
def expired_token_generator():
    def _generate(secret, user_id):
        return jwt.encode(
            {
                "exp": datetime.now(tz=timezone.utc) - timedelta(days=30),
                "iat": datetime.now(tz=timezone.utc) - timedelta(days=31),
                "sub": str(user_id),
            },
            secret,
            algorithm="HS256",
        )
    yield _generate


@pytest.fixture
def expired_refresh_token(existing_user, expired_token_generator, token_service):
    yield expired_token_generator(
        token_service.refresh_secret,
        existing_user.id,
    )


@pytest.fixture
def valid_refresh_token(existing_user, token_service):
    yield token_service.new_refresh_token(existing_user.id)


@pytest.fixture
def alt_valid_access_token(token_service):
    yield token_service.new_access_token(-1)


@pytest.fixture
def user_id_from_token(existing_user_tokens, token_service):
    user_id = token_service.decode_jwt(
        existing_user_tokens["access_token"],
        "access",
    )["sub"]
    yield int(user_id)


# ───────────────────────────────
# TASKS
# ───────────────────────────────

@pytest.fixture
def tasks_creator(app, task_service):
    def _create_tasks(user_id, tasks_data=None):
        default_tasks = [
            {"title": "Buy groceries", "description": "Buy milk, eggs, bread"},
            {"title": "Pay bills", "description": "Pay electricity and water bills"},
        ]
        tasks_data = tasks_data or default_tasks
        with app.app_context():
            for task in tasks_data:
                task_service.create_task(
                    user_id,
                    task["title"],
                    task["description"],
                )
    yield _create_tasks


@pytest.fixture
def task_id(app, task_service, user_id_from_token):
    with app.app_context():
        task = task_service.create_task(
            user_id_from_token,
            title="Foo",
            description="Bar"
        )
        yield task.id


@pytest.fixture
def task(app, task_service, task_id):
    with app.app_context():
        yield task_service.get_task(task_id)


@pytest.fixture
def access_token_of_user_with_tasks(
    existing_user_tokens,
    user_id_from_token,
    tasks_creator,
):
    tasks_creator(user_id_from_token)
    yield existing_user_tokens["access_token"]
