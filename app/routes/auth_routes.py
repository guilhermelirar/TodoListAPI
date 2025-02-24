#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.services import auth_service as serv

# Blueprint for register and login routes
auth_bp = Blueprint('auth', __name__) 

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

    token: str = serv.generate_token(new_user_id, email)
    print("New token issued: ", token)

    return jsonify({
        "token": token 
    }), 201
