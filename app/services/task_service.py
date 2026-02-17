# app/services/task_service.py 
from sqlalchemy.exc import IntegrityError
from app.models.task import Task, TaskStatus
from app.models.tag import Tag
from app import db
from app.errors import *
from sqlalchemy import text

class TaskService():
    def __init__(self, session):
        self.session = session

    def create_task(self, user_id: int, title: str, description: str = None):    
        if not title:
            raise TitleEmpty()

        try:
            task = Task(
                user_id=user_id, 
                title=title, 
                description=description
            )

            self.session.add(task)
            self.session.commit()

            return task

        except IntegrityError:
            self.session.rollback()
            raise UserNotFound()

        except Exception:
            self.session.rollback()
            raise


    def get_task(self, id: int) -> Task:
        task = self.session.query(Task)\
            .filter(Task.id == id)\
            .first()

        if not task:
            raise TaskNotFound()

        return task

    def get_or_create_tag(self, user_id, name) -> int:
        """
        Returns id of a tag owned by user (user_id) with given name

        Args:
            - user_id (int): id of tag owner
            - name (str): tag name

        Returns:
            - tag_id (int): id of tag
        """

        tag_id = self.session.execute(text("""
            SELECT id from tags 
            WHERE (name, user_id) = (:name, :user_id)
        """), {"name":name, "user_id":user_id}).scalar()

        if tag_id is None:
            tag_id = self.session.execute(text(
                """
                INSERT INTO tags (name, user_id)
                VALUES (:name, :user_id)
                RETURNING id
                """
            ), {"name":name, "user_id":user_id}).scalar()

        return tag_id

    def _update_task_tags(self, task: Task, tag_names: list[str]):
        if not isinstance(tag_names, list):
            raise ServiceError("Tags must be a list", 400)

        self.session.execute(text(
            """
            DELETE FROM task_tags 
            WHERE task_tags.task_id = :task_id
            """
        ), {"task_id": task.id})

        user_id = task.user_id

        for name in set(tag_names):
            name = name.strip().lower()
            if not name:
                continue

            tag_id = self.get_or_create_tag(user_id, name)
            
            # task.tags.append(tag)
            self.session.execute(text(
                """
                INSERT INTO task_tags (task_id, tag_id)
                VALUES (:task_id, :tag_id)
                """
            ), {"task_id": task.id, "tag_id": tag_id})

    def update_task(self, user_id: int, task_id: int, data: dict) -> dict:
        task = self.get_task(task_id)

        if task.user_id != user_id:
            raise Forbidden()

        allowed_fields = {
            "title": str,
            "description": str,
            "status": str,
            "tags": list[str]
        }

        for field, value in data.items():
            if field not in allowed_fields:
                raise ServiceError(f"Field '{field}' not allowed", 400)

            expected_type = allowed_fields[field]
            if not isinstance(value, expected_type):
                raise ServiceError(f"Field '{field}' must be {expected_type}", 400)

            if field == "status":
                try:
                    task.status = TaskStatus(value)
                except ValueError:
                    raise ServiceError(f"Status '{value}' not allowed", 400)

            elif field == "tags":
                self._update_task_tags(task, value)

            else:
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
