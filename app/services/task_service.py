# app/services/task_service.py 
from sqlalchemy.exc import IntegrityError
from app.models import Task
from app import db

class PermissionError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass

def create_task(user_id: int, data):
    new_task: Task
   
    title = data.get("title")
    if not title:
        raise ValueError("Title cannot be empty")

    try:
        new_task = Task(
            user_id=user_id, 
            title=title, 
            description=data.get("description"))

        db.session.add(new_task)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        raise ValueError("User does not exist")

    except:
        db.session.rollback()
        raise RuntimeError("An unexpected error has ocurred")
    
    return new_task.to_dict()




def update_task(user_id: int, task_id, data: dict) -> dict:
    """ 
    Updates task and return new data, or throw exceptions 
    if task not found or user doesn't have the permission
    """
    task = db.session.query(Task)\
    .filter(Task.id == task_id).first()

    if not task:
        raise TaskNotFoundError("Task not found")

    if task.user_id != user_id:
        raise PermissionError

    task.title = data["title"]
    task.description = data["description"]
    updated = {
        "id": task.id,
        "title": task.title,
        "description": task.description
    }
    db.session.commit()
    return updated


