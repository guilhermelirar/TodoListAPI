#app/utils.py 
"""
Utility decorator functions
"""
from functools import wraps
from flask import request, jsonify
from app.extensions import limiter

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

    if errors == []:
        return True, None
    
    return False, errors


def require_json_fields(required: set):
    """Ensures the request has a JSON with the required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"message": "Invalid request"}), 400

            request_fields_set = set(request.get_json().keys())
            missing_fields = required - request_fields_set

            if missing_fields:
                return jsonify({
                    "message": "Missing information", 
                    "details": list(missing_fields)
                }), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator
