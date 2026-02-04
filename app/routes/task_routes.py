#app/routes/task_routes.py
from flask import Blueprint, request, Response, jsonify, g
from app.utils import require_json_fields, validate_query_parameters
import app.services.task_service as serv
from app.services.token_service import user_from_access_token 
from app.utils import limit_requests, get_user_id

todo_bp = Blueprint('todos', __name__)

@todo_bp.route('/todos', methods=['POST'])
@limit_requests("50 per hour")
@require_json_fields(required={"title", "description"})
def todos() -> tuple[Response, int]:
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
              type: int
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
    user_id = get_user_id(request)
    created_item_details = serv.create_task(user_id, request.get_json())
    return jsonify(created_item_details), 201

@todo_bp.route("/todos/<int:id>", methods=['PUT'])
@limit_requests("50 per hour")
@require_json_fields(required={"title", "description"})
def update_task(id: int):
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

    responses:
      200:
        description: To do item updated successfully. New information is returned
        schema:
          type: object
          properties:
            id:
              type: int
              example: 1
            title:
              type: string
              example: "Buy groceries"
            description:
              type: string
              example: "Buy milk, eggs, bread and cheese"

      400:
        description: Bad request due to missing or invalid data
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid request"
      
      403:
        description: User has no permission toa access the resource
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Forbidden"

      404:
        description: Resource was not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Task not found"
    """

    new_data = serv.update_task(get_user_id(request), id, request.get_json())
    
    return jsonify(new_data), 200

@todo_bp.route('/todos/<int:id>', methods=['DELETE'])
@limit_requests("50 per hour")
def delete_task(id: int) -> tuple[Response, int]:
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
        description: To do item deleted successfully.

      403:
        description: User has no permisson toa access the resource
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Forbidden"

      404:
        description: Resource was not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Task not found"
    """
    serv.delete_task(get_user_id(request), id)
    
    return jsonify(), 204


@todo_bp.route('/todos', methods=['GET'])
@limit_requests("500 per hour")
def get_tasks():
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
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
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
                        example: "Buy milk, eggs, bread"
                page:
                  type: integer
                  example: 1
                limit:
                  type: integer
                  example: 10
                total:
                  type: integer
                  example: 2

      400:
        description: Bad request due to invalid query parameters
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid request"
            errors:
              type: array
              items: 
                type: string
                example: "Invalid value for limit '-1' (should be higher than 0)" 
    """
    user_id = get_user_id(request)

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
