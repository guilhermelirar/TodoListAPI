#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify, g
from app.utils import require_json_fields, validate_query_parameters
import app.services.task_service as serv
from app.services.auth_service import user_from_access_token, UnauthorizedTokenError
from app.utils import limit_requests

todo_bp = Blueprint('todos', __name__)

@todo_bp.before_request
def require_authenticated(): 
    auth_header = request.headers.get('authorization')
    if not auth_header or len(auth_header.split()) != 2:
        return jsonify({
            "message": "Unauthorized"
        }), 401
         
    token = auth_header.split()[1]
        
    # Checks if the token is valid
    try:
        user_id = user_from_access_token(token)["sub"]
        g.user_id = int(user_id)
    except UnauthorizedTokenError as e:
        return jsonify({
            "message": str(e)
        }), 401

"""
POST /todos
{
  "title": "Buy groceries",
  "description": "Buy milk, eggs, and bread"
}
"""
@todo_bp.route('/todos', methods=['POST'])
@limit_requests("50 per hour")
@require_json_fields(required={"title", "description"})
def todos() -> tuple[Response, int]:
    try:
        created_item_details = serv.create_task(g.get("user_id"), request.get_json())
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
@limit_requests("50 per hour")
@require_json_fields(required={"title", "description"})
def update_task(id: int):
    try:
        new_data = serv.update_task(g.get("user_id"), id, request.get_json())
    
    except serv.TaskPermissionError:
        return jsonify({
            "message": "Forbidden"
        }), 403
    
    except serv.TaskNotFoundError as e:
        return jsonify({
            "message": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "message": "An unexpected error has ocurred"
        }), 500

    return jsonify(new_data), 200


"""
DELETE /todos/1
"""
@todo_bp.route('/todos/<int:id>', methods=['DELETE'])
@limit_requests("50 per hour")
def delete_task(id: int) -> tuple[Response, int]:
    try:
        serv.delete_task(g.get("user_id"), id)
    
    except serv.TaskNotFoundError as e:
        return jsonify({
            "message": str(e)
        }), 404
    
    except serv.TaskPermissionError as e:
        return jsonify({
            "message": "Forbidden"
        }), 403

    except Exception:
        return jsonify({
            "message": "An unexpected error has ocurred"
        }), 500

    return jsonify(), 204


"""
GET /todos?page=1&limit=10
"""
@todo_bp.route('/todos', methods=['GET'])
@limit_requests("500 per hour")
def get_tasks():
    valid_query, errors = validate_query_parameters()

    page = int(request.args["page"])
    limit = int(request.args["limit"])

    if not valid_query:
        return jsonify({
            "message": "Invalid request",
            "errors": errors
        }), 400

    data = serv.tasks_by_user_id(g.get("user_id"), page, limit)
    
    total: int = serv.count_tasks_by_user_id(g.get("user_id"))
    data_in_page = data[0:limit]
    data_in_dict = [item.to_dict() for item in data_in_page]

    return jsonify({
        "data": data_in_dict,
        "page": page,
        "limit": limit,
        "total": total
    }), 200
