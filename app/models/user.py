# app/models/user.py
import re
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @staticmethod
    def is_email_valid(email: str) -> bool:
        regex = r"^[\w\.-]+@([\w\-]+\.)+[\w\-]{2,4}$"
        return bool(re.match(regex, email))
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __init__(self, name, email, password):
        if not User.is_email_valid(email):
            raise ValueError("Invalid Email")
        
        self.name = name 
        self.email = email
        self.password = generate_password_hash(password)
