import jwt
from app.errors import InvalidToken, ExpiredToken
from app.models import BlacklistedToken
import hashlib
from datetime import datetime, timedelta, timezone
from app import db

class TokenManager():
    def __init__(self, ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET):
        self.ACCESS_TOKEN_SECRET = ACCESS_TOKEN_SECRET
        self.REFRESH_TOKEN_SECRET = REFRESH_TOKEN_SECRET
        self.algorithm = "HS256"

    def generate_access_token(self, user_id: int) -> str:
        exp = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
        return jwt.encode({
            "sub": str(user_id), 
            "exp": exp,
        }, self.ACCESS_TOKEN_SECRET, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: int) -> str:
        exp = datetime.now(tz=timezone.utc) + timedelta(days=30)
        return jwt.encode({
            "sub": str(user_id), 
            "exp": exp,
        }, self.REFRESH_TOKEN_SECRET, algorithm=self.algorithm)


    def user_from_refresh_token(self, token: str) -> dict:
        return user_from_token(token, REFRESH_TOKEN_SECRET)


    def user_from_access_token(self, token: str) -> dict:
        return user_from_token(token, ACCESS_TOKEN_SECRET)


    def user_from_token(self, token: str, secret: str) -> dict:
        try:
            return jwt.decode(token, secret, algorithms="HS256")
        
        except jwt.ExpiredSignatureError:
            raise ExpiredToken()

        except jwt.InvalidTokenError:
            raise InvalidToken()

        except Exception:
            raise RuntimeError()

    def blacklist_token(self, token: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        try:
            decoded = jwt.decode(token)
            expires_at = datetime.fromtimestamp(decoded['exp'])
        
        except:
            raise InvalidToken()

        existing = BlacklistedToken.query\
            .filter_by(token_hash=token_hash)\
                .first()
        
        if existing:
            return

        blacklisted = BlacklistedToken(
            token_hash = token_hash, 
            expires_at = expires_at
        )

        db.session.add(blacklisted)
        db.session.commit()

    def is_token_blacklisted(self, token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        entry = BlacklistedToken.query.filter_by(
            token_hash=token_hash
        ).first()

        if not entry:
            return False

        if entry.expires_at < datetime.utcnow():
            db.session.delete(entry)
            db.session.commit()
            return False

        return True

    def cleanup_blacklist(self):
        BlacklistedToken.query.filter(
            BlacklistedToken.expires_at < datetime.utcnow()
        ).delete()

        db.session.commit()