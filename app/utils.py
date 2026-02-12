"""
Utility decorator functions
"""
from functools import wraps
from flask import request, jsonify, current_app
from app.extensions import limiter
from app.errors import InvalidToken, Unauthorized
import json


def limit_requests(limit: str):
    def decorator(f):
        @wraps(f)
        @limiter.limit(limit)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return decorator


def validate_query_parameters():
    errors = []
    allowed_params = {"page", "limit"}
    received_params = set(request.args.keys())
    extra_params = received_params - allowed_params

    page = int(request.args.get("page", "1"))
    limit = int(request.args.get("limit", "10"))

    if page < 1:
        errors.append(f"Invalid value for page '{page}' (should be higher than 0)")

    if limit < 1:
        errors.append(f"Invalid value for limit '{limit}' (should be higher than 0)")

    if extra_params:
        errors.append(f"Unexpected parameters: {', '.join(extra_params)}")

    if not errors:
        return True, None

    return False, errors


def require_json_fields(required: set):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            raw = request.get_data(as_text=True)

            try:
                data = json.loads(raw)
            except Exception:
                return jsonify({"message": "Invalid JSON body"}), 400

            missing_fields = required - set(data.keys())

            if missing_fields:
                return jsonify({
                    "message": "Missing information",
                    "details": list(missing_fields),
                }), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def get_jwt(request) -> str:
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise Unauthorized()

    token = auth_header.split(" ")[1]

    token_service = current_app.token_service

    if token_service.is_token_blacklisted(token):
        raise InvalidToken("Blacklisted Token")

    return token


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token_service = current_app.token_service
        user_id = token_service.decode_jwt(
            get_jwt(request)
        )["sub"]
        return f(user_id=int(user_id), *args, **kwargs)
    return wrapper