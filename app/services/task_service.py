# app/services/task_service.py 
from sqlalchemy.exc import IntegrityError
from app.models.task import Task, TaskStatus
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

        except Exception:
            self.session.rollback()
            raise

        return new_task.to_dict()

    def get_task(self, id: int) -> Task:
        task = self.session.query(Task)\
            .filter(Task.id == id)\
            .first()

        if not task:
            raise TaskNotFound()

        return task

    def update_task(self, user_id: int, task_id: int, data: dict) -> dict:
        task = self.get_task(task_id)

        if task.user_id != user_id:
            raise Forbidden()

        allowed_fields = {
            "title": str,
            "description": str,
            "status": str,
        }

        for field, value in data.items():
            if field not in allowed_fields:
                raise ServiceError(f"Field '{field}' not allowed", 400)

            if field == "status":
                try:
                    value = TaskStatus(value)
                except ValueError:
                    raise ServiceError(f"Status '{value}' not allowed", 400)

            setattr(task, field, value)

        self.session.commit()
        return task.to_dict()

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
