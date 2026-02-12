# app/services/token_service.py
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from app.errors import InvalidToken, ExpiredToken, ServiceError
from app.models import BlacklistedToken
from sqlalchemy import text

class TokenService():
    def __init__(self, db, access_secret: str, refresh_secret: str):
        self.algorithm = "HS256"
        self.access_secret = access_secret
        self.refresh_secret = refresh_secret
        self.db = db

    def new_access_token(self, sub: str) -> str:
        """
        Generates access token with identifier in passed in sub.
        Expires in 15 minutes
        """
        exp = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        return jwt.encode({
            "sub": str(sub),
            "exp": exp
        }, self.access_secret, self.algorithm)

    def new_refresh_token(self, sub: str):
        """
        Generates refresh token with identifier in passed in sub.
        Expires in 30 days
        """
        exp = datetime.now(tz=timezone.utc) + timedelta(days=30)
        return jwt.encode({
            "sub": str(sub),
            "exp": exp
        }, self.refresh_secret, self.algorithm)

    def decode_jwt(self, token: str, type="access") -> dict:
        """
        Returns the payload of a JSON web token. 
        Raises exceptions if invalid or expired token given.
        
        Args:
            token (str): JWT in string format
            type (str): type of the token ("access" or "refresh", case-sensitive)

        Returns:
            payload (dict)

        Raises:
            ValueError: if "type" given is not 'access' or 'refresh'
            ExpiredToken: if token already expired
            InvalidToken: if given string is not a JWT or is not coded with the "type" given
        """
        if type == "access":
            secret = self.access_secret
        elif type == "refresh":
            secret = self.refresh_secret
        else:
            raise ValueError("Invalid token type")

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=[self.algorithm]
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise ExpiredToken("Token expired")

        except jwt.InvalidTokenError:
            raise InvalidToken("Invalid token")

    def blacklist_refresh_token(self, token: str) -> None:
        """
        Puts given refresh token into a list of Blacklisted tokens

        Args:
            token (str): string of access JWT

        Raises:
            Exceptions raised by decode_jwt        
        """

        hash = hashlib.sha256(token.encode()).hexdigest()
        
        if self.is_token_blacklisted(token):
            return 

        decoded = self.decode_jwt(token, "refresh")

        expires_at = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        
        blacklisted = BlacklistedToken(
            token_hash = hash,
            expires_at = expires_at
        )

        self.db.add(blacklisted)
        self.db.commit()

    def is_token_blacklisted(self, token: str) -> bool:
        """Returns True if a token is blacklisted and False if not"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        entry = self.db.query(BlacklistedToken).filter_by(
            token_hash=token_hash
        ).first()

        if not entry:
            return False

        if entry.expires_at.tzinfo is None:
            expires_at_aware = entry.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_aware = entry.expires_at

        if expires_at_aware < datetime.now(tz=timezone.utc):
            self.db.delete(entry)
            self.db.commit()
            return False

        return True

    def cleanup_blacklist(self) -> None:
        """
        Clean up token blacklist removing expired tokens
        """

        self.db.execute(
            text("""
            DELETE FROM blacklisted_tokens
            WHERE expires_at < now()
            """)
        )
