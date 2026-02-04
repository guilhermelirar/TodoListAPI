#app/services/auth_service.py
from typing import Union
from app.errors import *
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError

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

def login(email, password) -> Union[int, None]:
    user = db.session.query(User).filter(User.email == email).first()
    if user == None or not user.check_password(password):
        return None
    
    return user.id
