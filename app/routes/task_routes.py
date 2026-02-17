# app/routes/task_routes.py
from flask import Blueprint, request, Response, jsonify, current_app
from app.utils import require_json_fields, validate_query_parameters
from app.utils import limit_requests, login_required

todo_bp = Blueprint('todos', __name__)


@todo_bp.route('/todos', methods=['POST'])
@limit_requests("50 per hour")
@require_json_fields(required={"title", "description"})
@login_required
def create_todo(user_id: int) -> tuple[Response, int]:
    """
    Create a new task
    ---
    tags:
      - Tasks
    parameters:
      - name: Authorization
        in: header
        description: Bearer access token
        required: true
        type: string
        example: Bearer valid_access_token

      - name: new_task
        in: body
        description: Required information to create a new to do item
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Buy groceries"
            description:
              type: string
              example: "Buy milk, eggs, and bread"

    responses:
      201:
        description: To do item created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "Buy groceries"
            description:
              type: string
              example: "Buy milk, eggs, and bread"

      400:
        description: Bad request due to missing or invalid data
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid request"
    """
    task_service = current_app.task_service
    data = request.get_json()

    created_item = task_service.create_task(
        user_id,
        data["title"],
        data["description"],
    )

    return jsonify(created_item), 201


@todo_bp.route("/todos/<int:id>", methods=['PATCH'])
@limit_requests("50 per hour")
@login_required
def update_task(user_id: int, id: int) -> tuple[Response, int]:
    """
    Update an existing task
    ---
    tags:
      - Tasks
    parameters:
      - name: Authorization
        in: header
        description: Bearer access token
        required: true
        type: string
        example: Bearer valid_access_token

      - name: id
        in: path
        description: ID of the to do item
        required: true
        schema:
          type: integer
          example: 1

      - name: new_information
        in: body
        description: Required information to update a to-do item
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Buy groceries"
            description:
              type: string
              example: "Buy milk, eggs, bread and cheese"
            status:
              type: "done" | "todo"
              example: "done"

    responses:
      204:
        description: To do item updated successfully.
      400:
        description: Bad request due to missing or invalid data
      403:
        description: User has no permission to access the resource
      404:
        description: Resource was not found
    """

    task_service = current_app.task_service

    updated_data = task_service.update_task(
        user_id,
        id,
        request.get_json()
    )

    return jsonify(updated_data), 204


@todo_bp.route('/todos/<int:id>', methods=['DELETE'])
@limit_requests("50 per hour")
@login_required
def delete_task(user_id: int, id: int) -> tuple[Response, int]:
    """
    Delete an existing task
    ---
    tags:
      - Tasks
    parameters:
      - name: Authorization
        in: header
        description: Bearer access token
        required: true
        type: string
        example: Bearer valid_access_token

      - name: id
        in: path
        description: ID of the to do item
        required: true
        schema:
          type: integer
          example: 1

    responses:
      204:
        description: To do item deleted successfully
      403:
        description: User has no permission to access the resource
      404:
        description: Resource was not found
    """
    task_service = current_app.task_service
    task_service.delete_task(user_id, id)

    return jsonify(), 204


@todo_bp.route('/todos', methods=['GET'])
@limit_requests("500 per hour")
@login_required
def get_tasks(user_id: int) -> tuple[Response, int]:
    """
    Get list of todos with pagination
    ---
    tags:
      - Tasks
    parameters:
      - name: Authorization
        in: header
        description: Bearer access token
        required: true
        type: string
        example: Bearer valid_access_token

      - name: page
        in: query
        description: Page number for pagination
        required: false
        schema:
          type: integer
          example: 1

      - name: limit
        in: query
        description: Number of items per page
        required: false
        schema:
          type: integer
          example: 10

    responses:
      200:
        description: A paginated list of todos
      400:
        description: Bad request due to invalid query parameters
    """
    task_service = current_app.task_service

    valid_query, errors = validate_query_parameters()

    if not valid_query:
        return jsonify({
            "message": "Invalid request",
            "errors": errors
        }), 400

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    tasks = task_service.tasks_by_user_id(user_id, page, limit)
    total = task_service.count_tasks_by_user_id(user_id)

    data_in_dict = [task.to_dict() for task in tasks]

    return jsonify({
        "data": data_in_dict,
        "page": page,
        "limit": limit,
        "total": total
    }), 200