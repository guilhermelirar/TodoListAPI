# app/services/task_service.py 
from sqlalchemy.exc import IntegrityError
from app.models import Task
from app import db
from app.errors import *

class TaskService():
    def __init__(self, session):
        self.session = session

    def create_task(self, user_id: int, title: str, description: str = None):    
        if not title:
            raise TitleEmpty()

        new_task: Task
        try:
            new_task = Task(
                user_id=user_id, 
                title=title, 
                description=description
            )

            self.session.add(new_task)
            self.session.commit()

        except IntegrityError:
            self.session.rollback()
            raise UserNotFound()

        except:
            self.session.rollback()
    
        return new_task.to_dict()

    def get_task(self, id: int) -> Task:
        task = self.session.query(Task)\
            .filter(Task.id == id)\
            .with_for_update()\
            .first()

        if not task:
            raise TaskNotFound()

        return task

    def update_task(self, user_id: int, task_id, data: dict) -> dict:
        task = self.get_task(task_id)

        if task.user_id != user_id:
            raise Forbidden()

        task.title = data["title"]
        task.description = data["description"]
        updated = {
            "id": task.id,
            "title": task.title,
            "description": task.description
        }
        self.session.commit()
        return updated

    def delete_task(self, user_id: int, task_id: int):
        task = self.get_task(task_id)

        if task.user_id != user_id:
            raise Forbidden()

        self.session.delete(task)
        self.session.commit()


    def count_tasks_by_user_id(self, user_id: int):
        return self.session.query(Task).filter(Task.user_id == user_id).count()    


    def tasks_by_user_id(self, user_id: int, page: int, limit: int):
        return self.session.query(Task)\
            .filter(Task.user_id == user_id)\
            .limit(limit)\
            .offset((page - 1) * limit)\
            .all()
