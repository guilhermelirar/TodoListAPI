#app/utils.py 
"""
Utility decorator functions
"""
from functools import wraps
from flask import request, jsonify
from app.services.auth_service import user_from_access_token, UnauthorizedTokenError

def require_auth(f):
    """ Ensures that the request header contains a valid jwt before proceeding with the operation """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checks if request has authorization header
        auth_header = request.headers.get('authorization')
        if not auth_header or len(auth_header.split()) != 2:
            return jsonify({
                "message": "Unauthorized"
            }), 401
        
        token = auth_header.split()[1]
        
        # Checks if the token is valid
        try:
            user_id = int(user_from_access_token(token)["sub"])
        except UnauthorizedTokenError as e:
            return jsonify({
                "message": str(e)
            }), 401
        
        return f(user_id, *args, **kwargs)

    return decorated_function


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
 
