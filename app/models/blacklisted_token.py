from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from app.models import User
from datetime import datetime

class BlacklistedToken(db.Model):
    __tablename__ = "blacklisted_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    def __repr__(self):
        return f'<BlacklistedToken {self.token_hash[:8]}...>'
    