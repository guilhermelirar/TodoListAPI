from app.models import User
from pytest import raises

def test_email_validation():
    name = "Name"
    email = "invalid email"
    password = "password123"

    with raises(ValueError, match='Invald Email'):
        User(name, email, password)
