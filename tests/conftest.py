# Adding to PYTHONPATH
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import pytest
from app import create_app, db
from app.models import User

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

    return new_user
