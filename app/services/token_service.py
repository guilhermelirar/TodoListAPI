# app/services/token_service.py
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from app import db
from app.errors import InvalidToken, ExpiredToken
from app.models import BlacklistedToken

ACCESS_TOKEN_SECRET = None
REFRESH_TOKEN_SECRET = None
ALGORITHM = "HS256"

def init(access_secret, refresh_secret):
    global ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET
    ACCESS_TOKEN_SECRET = access_secret
    REFRESH_TOKEN_SECRET = refresh_secret

def generate_access_token(user_id: int) -> str:
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    return jwt.encode({
        "sub": str(user_id), 
        "exp": exp,
    }, ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)

def generate_refresh_token(user_id: int) -> str:
    exp = datetime.now(tz=timezone.utc) + timedelta(days=30)
    return jwt.encode({
        "sub": str(user_id), 
        "exp": exp,
    }, REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)

def user_from_refresh_token(token: str) -> int:
    return int(decode_token(token, REFRESH_TOKEN_SECRET)["sub"])

def user_from_access_token(token: str) -> int:
    return int(decode_token(token, ACCESS_TOKEN_SECRET)["sub"])

def decode_token(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    
    except jwt.ExpiredSignatureError:
        raise ExpiredToken()

    except jwt.InvalidTokenError:
        raise InvalidToken()

    except Exception:
        raise RuntimeError()

def blacklist_token(token: str):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        decoded = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)
    
    except:
        try:
            decoded = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=["HS256"])
            expires_at = datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)
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

def is_token_blacklisted(token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    entry = BlacklistedToken.query.filter_by(
        token_hash=token_hash
    ).first()

    if not entry:
        return False

    if entry.expires_at.tzinfo is None:
        expires_at_aware = entry.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at_aware = entry.expires_at

    if expires_at_aware < datetime.now(tz=timezone.utc):
        db.session.delete(entry)
        db.session.commit()
        return False

    return True

def cleanup_blacklist():
    BlacklistedToken.query.filter(
        BlacklistedToken.expires_at < datetime.now(tz=timezone.utc)
    ).delete()

    db.session.commit()