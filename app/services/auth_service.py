#app/services/auth_service.py
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import jwt, os

ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'
REFRESH_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'

class UserAlreadyExistsError(Exception):
    pass

def generate_access_token(id: int, email: str) -> str:
    return jwt.encode({
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30),
        "id": id, 
        "email": email}, ACCESS_TOKEN_SECRET, algorithm="HS256")

def generate_refresh_token(id: int, email: str) -> str:
    return jwt.encode({
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=30),
        "id": id, 
        "email": email
    }, REFRESH_TOKEN_SECRET, algorithm="HS256")

def create_user(name: str, email: str, password: str) -> int:
    new_user: User
    
    try:
        new_user = User(name, email, password)
    except ValueError as ve:
        print("Value error:", ve.args)
        raise
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user.id

    except IntegrityError as ie:
        print("Integrity error:", ie.args)
        raise UserAlreadyExistsError("Email already in use")
    
    except Exception as e:
        print("Generic error:", e.args)
        raise RuntimeError("Unknown error ocurred while creating the user")
