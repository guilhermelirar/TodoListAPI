#app/services/auth_service.py
from app.errors import EmailAlreadyInUse, InvalidCredentials
from app.models import User
from sqlalchemy.exc import IntegrityError
import re

class AccountService():
    def __init__(self, db_session):
        self.db_session = db_session

    def _validate_user_credentials(self, user, password) -> None:
        if (
            user is None
            or not user.check_password(password)
        ):
            raise InvalidCredentials()

    def _get_user(self, user_id: int):
        return (
            self.db_session
            .query(User)
            .filter(User.id == user_id)
            .first()
        )

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
        user = (
            self.db_session
            .query(User)
            .filter(User.email == email)
            .first()
        )

        self._validate_user_credentials(user, password)
        return user.id


    def check_password(self, user_id, password) -> None:
        user = self._get_user(user_id)
        self._validate_user_credentials(user, password)

    def delete_self(self, user_id: int, password: str) -> None:
        user = self._get_user(user_id)
        self._validate_user_credentials(user, password)

        self.db_session.delete(user)
        self.db_session.commit()

