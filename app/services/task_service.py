# app/services/task_service.py 
from sqlalchemy.exc import IntegrityError
from app.models import Task
from app import db

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
