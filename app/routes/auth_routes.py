#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.services import auth_service as serv
from app.utils import require_json_fields

# Blueprint for register and login routes
auth_bp = Blueprint('auth', __name__) 

@auth_bp.route('/refresh', methods=['POST'])
def refresh() -> tuple[Response, int]:
    headers = request.headers
    auth_header = headers.get("authorization")
    if not auth_header:
        return jsonify({
            "message": "Unauthorized"
        }), 401

    token = auth_header.split(' ')[1]
    
    try:
        data = serv.user_from_refresh_token(token)
        new_access_token = serv.generate_access_token(data["sub"])

        return jsonify({
            "token": new_access_token
        }), 200
    
    except serv.UnauthorizedTokenError as e:
        return jsonify({
            "message": str(e)
        }), 401

    except RuntimeError:
        return jsonify({
            "message": "Internal error"
        }), 500


""" POST /register
{
  "name": "John Doe",
  "email": "john@doe.com",
  "password": "password"
}
"""
@auth_bp.route('/register', methods=['POST'])
@require_json_fields(required={'name', 'email', 'password'})
def register() -> tuple[Response, int]:
    """ Registers a new user and returns with access and refresh token """
    new_user_id: int
    try:
        new_user_id = serv.create_user(request.get_json())
    except serv.UserAlreadyExistsError as e:
        return jsonify({
            "message": str(e)
        }), 400

    access_token: str = serv.generate_access_token(new_user_id)
    print("New access token issued: ", access_token)
    refresh_token: str = serv.generate_refresh_token(new_user_id)
    print("New refresh token issued: ", refresh_token)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201


"""
POST /login
{
  "email": "john@doe.com",
  "password": "password"
}
"""
@auth_bp.route('/login', methods=['POST'])
@require_json_fields(required={"email", "password"})
def login() -> tuple[Response, int]:
    tokens = serv.login(request.get_json()["email"], 
                        request.get_json()["password"])
    
    if not tokens:
        return jsonify({
            "message": "Invalid credentials"
        }), 404

    return jsonify(tokens), 200
