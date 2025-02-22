# app/models/user.py
import re
from sqlalchemy.orm import Mapped, mapped_column
from app import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)

    @staticmethod
    def is_email_valid(email: str) -> bool:
        regex = r"^[\w\.-]+@([\w\-]+\.)+[\w\-]{2,4}$"
        return bool(re.match(regex, email))
    
    def __init__(self, name, email, password):
        if not User.is_email_valid(email):
            raise ValueError("Invalid Email")
        
        self.name = name 
        self.email = email
        self.password = generate_password_hash(password)
