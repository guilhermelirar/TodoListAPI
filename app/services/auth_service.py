#app/services/auth_service.py
from typing import Union
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import jwt, os

ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'
REFRESH_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'

class UserAlreadyExistsError(Exception):
    pass

class UnauthorizedTokenError(Exception):
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
        raise UnauthorizedTokenError("Token expired, please login again.")

    except jwt.InvalidTokenError:
        raise UnauthorizedTokenError("Unauthorized")
    

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

def login(email, password) -> Union[dict, None]:
    user = db.session.query(User).filter(User.email == email).first()
    if user == None or not user.check_password(password):
        return None
    
    return {
        "access_token": generate_access_token(user.id, user.email),
        "refresh_token": generate_refresh_token(user.id, user.email)
    }
