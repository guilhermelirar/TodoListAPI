from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from app.models import User
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"

task_tags = db.Table(
    "task_tags",
    db.Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    db.Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Task(db.Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.TODO
    )

    user: Mapped["User"] = relationship(back_populates="tasks")

    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=task_tags,
        backref="tasks"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value
        }

    def __init__(self, user_id: int, title: str, description: str = ""):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.status = TaskStatus.TODO
