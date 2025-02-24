#app/services/auth_service.py
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError

class UserAlreadyExistsError(Exception):
    pass

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
