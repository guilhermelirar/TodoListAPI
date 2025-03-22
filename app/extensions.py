from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import g

def rate_limit_key():
    return str(g.get("user_id", get_remote_address()))

limiter = Limiter(
    rate_limit_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

