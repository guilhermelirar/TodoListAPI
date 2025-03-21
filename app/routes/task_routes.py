#app/routes/auth_routes.py
from flask import Blueprint, request, Response, jsonify
from app.utils import require_auth, require_json_fields, validate_query_parameters
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
@require_json_fields(required={"title", "description"})
def todos(user_id: int) -> tuple[Response, int]:
    try:
        created_item_details = serv.create_task(user_id, request.get_json())
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
@require_json_fields(required={"title", "description"})
def update_task(user_id: int, id: int):
    try:
        new_data = serv.update_task(user_id, id, request.get_json())
    
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
@require_auth
def delete_task(user_id: int, id: int) -> tuple[Response, int]:
    try:
        serv.delete_task(user_id, id)
    
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
@require_auth
def get_tasks(user_id: int):
    valid_query, errors = validate_query_parameters()

    page = int(request.args["page"])
    limit = int(request.args["limit"])

    if not valid_query:
        return jsonify({
            "message": "Invalid request",
            "errors": errors
        }), 400

    data = serv.tasks_by_user_id(user_id, page, limit)
    
    total: int = serv.count_tasks_by_user_id(user_id)
    data_in_page = data[0:limit]
    data_in_dict = [item.to_dict() for item in data_in_page]

    return jsonify({
        "data": data_in_dict,
        "page": page,
        "limit": limit,
        "total": total
    }), 200
