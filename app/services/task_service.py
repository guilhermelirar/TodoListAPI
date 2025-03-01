# app/services/task_service.py 
from app.models import Task
from app import db

def create_task(user_id: int, data):
    new_task: Task
    
    try:
        new_task = Task(
            user_id=user_id, 
            title=data["title"], 
            description=data.get("description"))

    except ValueError as ve:
        print("Value error:", ve.args)
        raise
    
    db.session.add(new_task)
    db.session.commit()
    return new_task.to_dict() 
