from app.models import User
from pytest import raises

def test_email_validation():
    name = "Name"
    email = "invalid email"
    password = "password123"

    with raises(ValueError, match="Invalid Email"):
        User(name, email, password)

def test_password_is_hashed():
    name = "Name"
    email = "valid@email.com"
    password = "password123"

    user = User(name, email, password)
    assert user.name == name
    assert user.email == email
    assert user.password != password
