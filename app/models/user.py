# app/models/user.py
import re
from sqlalchemy.orm import Mapped, mapped_column
from app import db

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
