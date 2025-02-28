#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.services import auth_service as serv

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
        new_access_token = serv.generate_access_token(data["id"], data["email"])

        return jsonify({
            "token": new_access_token
        }), 200
    
    except serv.UnauthorizedTokenError as e:
        return jsonify({
            "message": str(e)
        }), 401


""" POST /register
{
  "name": "John Doe",
  "email": "john@doe.com",
  "password": "password"
}
"""
@auth_bp.route('/register', methods=['POST'])
def register() -> tuple[Response, int]:
    # Only accepts application/json
    if request.mimetype != 'application/json':
        return jsonify({
            "message": "Invalid request"
        }), 400
   
    # Required fields
    name: str = request.get_json().get("name", None)
    email: str = request.get_json().get("email", None)
    password: str = request.get_json().get("password", None)

    # Checking if all fields present
    if not name or not email or not password:
        return jsonify({
            "message" : "Missing information"
        }), 400

    new_user_id: int
    try:
        new_user_id = serv.create_user(name, email, password)
    except serv.UserAlreadyExistsError as e:
        return jsonify({
            "message": str(e)
        }), 400

    access_token: str = serv.generate_access_token(new_user_id, email)
    print("New access token issued: ", access_token)
    refresh_token: str = serv.generate_refresh_token(new_user_id, email)
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
def login() -> tuple[Response, int]:
    # Posssible invalid request
    if request.mimetype != 'application/json':
        return jsonify({
            "message": "Invalid request"
        }), 400

    # Required fields
    email: str = request.get_json().get("email", None)
    password: str = request.get_json().get("password", None)
    
    # Checking if all fields present
    if not email or not password:
        return jsonify({
            "message" : "Missing information"
        }), 400

    tokens = serv.login(email, password)
    if not tokens:
        return jsonify({
            "message": "Invalid credentials"
        }), 404

    return jsonify(tokens), 200
