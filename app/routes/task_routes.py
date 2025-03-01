#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify

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
    unauthorized = jsonify({
            "message": "Unauthorized"
        }), 401

    auth_header = request.headers.get('authorization')
    if not auth_header or len(auth_header.split())!=2:
        return unauthorized

    token: str = auth_header.split()[1]

    return jsonify(), 0
