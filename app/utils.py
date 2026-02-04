#app/utils.py 
"""
Utility decorator functions
"""
from functools import wraps
from flask import request, jsonify
from app.extensions import limiter
from app.services import token_service
from app.errors import ServiceError, InvalidToken

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


from flask import request, jsonify
import json

def require_json_fields(required: set):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            raw = request.get_data(as_text=True)

            try:
                data = json.loads(raw)
            except Exception:
                return jsonify({"message": "Invalid JSON body"}), 400

            request_fields_set = set(data.keys())
            missing_fields = required - request_fields_set

            if missing_fields:
                return jsonify({
                    "message": "Missing information",
                    "details": list(missing_fields)
                }), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def get_user_id(request):
    auth_header = request.headers.get('authorization')
        
    if not auth_header:
        raise ServiceError("Unauthorized", 401)

    token = auth_header.split(' ')[1]
            
    if token_service.is_token_blacklisted(token):
        raise InvalidToken()

    data = token_service.user_from_access_token(token)
    
    return int(data['sub'])
            