#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.utils import require_auth 
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
@require_auth
def todos(user: dict) -> tuple[Response, int]:
    if not request.is_json:
        return jsonify({
            "message": "Invalid request"
        }), 400

    data = request.get_json()
    if not data or not all(k in data for k in ("title", "description")):
        return jsonify({
            "message": "Missing fields"
        }), 400
    
    try:
        created_item_details = serv.create_task(user["id"], data)
        return jsonify(created_item_details), 201
    
    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except RuntimeError as re:
        return jsonify({
            "message": str(re)
        }), 500


"""
PUT /todos/1
{
  "title": "Buy groceries",
  "description": "Buy milk, eggs, bread, and cheese"
}
"""
@todo_bp.route("/todos/<int:id>", methods=['PUT'])
@require_auth
def update_task(user: dict, id: int): 
    return jsonify({
        "message": id
    }), 0

