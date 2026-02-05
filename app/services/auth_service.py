#app/services/auth_service.py
from app.errors import EmailAlreadyInUse, InvalidCredentials
from app.models import User
from sqlalchemy.exc import IntegrityError
import re

class AccountService():
    def __init__(self, db_session):
        self.db_session = db_session

    def validate_email(self, email: str):
        regex = r"^[\w\.-]+@([\w\-]+\.)+[\w\-]{2,4}$"
        if not re.match(regex, email):
            raise ValueError("Invalid email")

    def create_user(self, name: str, email: str, password: str) -> int:
        """
        Returns the id of a new User created with user_data
        Assumes user_data contains the required fields
        """
        
        self.validate_email(email)

        new_user = User(name, email, password)
        
        try:
            self.db_session.add(new_user)
            self.db_session.commit()
            return new_user.id

        except IntegrityError as ie:
            print("Integrity error:", ie.args)
            raise EmailAlreadyInUse()

    def get_user_id(self, email, password) -> int:
        user = self.db_session.query(User).filter(User.email == email).first()
        
        if user == None or not user.check_password(password):
            raise InvalidCredentials()
        
        return user.id
