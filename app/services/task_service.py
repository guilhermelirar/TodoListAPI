# app/services/task_service.py 
from sqlalchemy.exc import IntegrityError
from app.models import Task
from app import db

class TaskPermissionError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass


def get_task_for_modification(user_id: int, task_id: int) -> Task:
    """
    Fetch task from database using task_id, for further modification
    by other functions (update and delete). Raise exceptions
    if not found (TaskNotFoundError), or if user_id does not match
    with the resource owner (TaskPermissionError).
    """
    task = db.session.query(Task)\
    .filter(Task.id == task_id)\
    .with_for_update()\
    .first()

    if not task:
        raise TaskNotFoundError("Task not found")

    if task.user_id != user_id:
        raise TaskPermissionError

    return task


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
    Updates task title and description. Doesn't handle
    exceptions raised by get_task_for_modification
    """
    task = get_task_for_modification(user_id, task_id)

    task.title = data["title"]
    task.description = data["description"]
    updated = {
        "id": task.id,
        "title": task.title,
        "description": task.description
    }
    db.session.commit()
    return updated


def delete_task(user_id: int, task_id: int):
    """ 
    Deletes a task from database. Doesn't handle
    exceptions raised by get_task_for_modification
    """
    task = get_task_for_modification(user_id, task_id)
    db.session.delete(task)
    db.session.commit()


def count_tasks_by_user_id(user_id: int):
   return db.session.query(Task).filter(Task.user_id == user_id).count()    


def tasks_by_user_id(user_id: int, page: int, limit: int):
    return db.session.query(Task)\
        .filter(Task.user_id == user_id)\
        .limit(limit)\
        .offset((page - 1) * limit)\
        .all()
