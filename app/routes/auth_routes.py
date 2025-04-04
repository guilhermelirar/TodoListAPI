#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.services import auth_service as serv
from app.utils import require_json_fields
from app.extensions import limiter

# Blueprint for register and login routes
auth_bp = Blueprint('auth', __name__) 

@auth_bp.route('/refresh', methods=['POST'])
def refresh() -> tuple[Response, int]:
    """
    Receive access token
    ---
    tags:
      - Auth
    parameters:
      - name: Authorization
        in: header
        description: Bearer refresh token
        required: true
        type: string
        example: Bearer valid_refresh_token

    responses:
      200:
        description: Successfull access token generation
        schema:
          type: object
          properties:
            token:
              type: string
              example: "abcdefghlmnop1"

      401:
        description: Unauthorized due to invalid, missing or expired token
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Unauthorized"
        examples:
          invalid_token:
            value:
                message: "Unauthorized"
          expired_token:
            value:
                message: "Token expired, please login again"
    """

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


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
@require_json_fields(required={'name', 'email', 'password'})
def register() -> tuple[Response, int]:
    """
    Register a new user
    ---
    tags:
      - Auth
    parameters:
      - name: user_data
        in: body
        description: Required information to create a new user
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "New User"
            email:
              type: string
              example: "validemail@email.com"
            password:
              type: string
              example: "verysafepassword123"

    responses:
      201:
        description: Account created successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "abcdefghlmnop1"
            refresh_token:
              type: string
              example: "abcdefghlmnop1"

      400:
        description: Bad request due to missing or invalid data
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid data"
            details:
              type: array
              items:
                type: string
        examples:
          invalid_data:
            value:
              message: "Invalid request"
          missing_information:
            value:
              message: "Missing information"
              details: ["email", "password"]
          email_in_use:
            value:
              message: "Email already in use"
    """
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


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
@require_json_fields(required={"email", "password"})
def login() -> tuple[Response, int]:
    """
    Login with user
    ---
    tags:
      - Auth
    parameters:
      - name: login_data
        in: body
        description: Required information to login
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "registered@email.com"
            password:
              type: string
              example: "validpassword123"

    responses:
      201:
        description: Successfull login
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "abcdefghlmnop1"
            refresh_token:
              type: string
              example: "abcdefghlmnop1"

      400:
        description: Bad request due to missing or invalid data
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid request"
      404:
        description: User with provided credentials does not exist 
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid credentials"
    """

    tokens = serv.login(request.get_json()["email"], 
                        request.get_json()["password"])
    
    if not tokens:
        return jsonify({
            "message": "Invalid credentials"
        }), 404

    return jsonify(tokens), 200
