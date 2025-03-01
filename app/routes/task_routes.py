#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.services.auth_service import user_from_access_token, UnauthorizedTokenError
import app.services.task_service as serv

todo_bp = Blueprint('todos', __name__)

"""
POST /todos
{
  "title": "Buy groceries",
  "description": "Buy milk, eggs, and bread"
}
"""
@todo_bp.route('/todos', methods=['POST'])
def todos() -> tuple[Response, int]:
    auth_header = request.headers.get('authorization')
    if not auth_header or len(auth_header.split()) != 2:
        return jsonify({
            "message": "Unauthorized"
        }), 401

    token: str = auth_header.split()[1]
    
    if not request.is_json:
        return jsonify({
            "message": "Invalid request"
        }), 400
    
    user: dict

    try:
        user = user_from_access_token(token)
    except UnauthorizedTokenError as e:
        return jsonify({
            "message": str(e)
        }), 401

    data = request.get_json()
    if not data or not all(k in data for k in ("title", "description")):
        return jsonify({
            "message": "Missing fields"
        }), 400
    
    try:
        created_item_details = serv.create_task(user["id"], data)
        return jsonify(created_item_details), 201
    except ValueError:
        return jsonify(), 0
