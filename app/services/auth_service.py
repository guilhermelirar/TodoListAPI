#app/services/auth_service.py
from typing import Union
from app.errors import *
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import jwt, os

ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'
REFRESH_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'

def generate_access_token(user_id: int) -> str:
    return jwt.encode({
            "sub": str(user_id), 
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30),
        }, ACCESS_TOKEN_SECRET, algorithm="HS256")


def generate_refresh_token(user_id: int) -> str:
    return jwt.encode({
        "sub": str(user_id), 
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=30),
    }, REFRESH_TOKEN_SECRET, algorithm="HS256")


def user_from_refresh_token(token: str) -> dict:
    return user_from_token(token, REFRESH_TOKEN_SECRET)

def user_from_access_token(token: str) -> dict:
    return user_from_token(token, ACCESS_TOKEN_SECRET)

def user_from_token(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, 
                          secret, 
                          algorithms="HS256")
    
    except jwt.ExpiredSignatureError:
        raise ExpiredToken()

    except jwt.InvalidTokenError:
        raise InvalidToken()

    except Exception:
        raise RuntimeError()
    

def create_user(user_data: dict) -> int:
    """
    Returns the id of a new User created with user_data
    Assumes user_data contains the required fields
    """
    
    try:
        new_user = User(user_data["name"], 
                        user_data["email"], 
                        user_data["password"])
    except ValueError as ve:
        print("Value error:", ve.args)
        raise
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user.id

    except IntegrityError as ie:
        print("Integrity error:", ie.args)
        raise EmailAlreadyInUse()

def login(email, password) -> Union[dict, None]:
    user = db.session.query(User).filter(User.email == email).first()
    if user == None or not user.check_password(password):
        return None
    
    return {
        "access_token": generate_access_token(user.id),
        "refresh_token": generate_refresh_token(user.id)
    }
