from typing import List
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import datetime as dt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    tasklist: Mapped["TaskList"] = relationship(back_populates="author")


class TaskList(db.Model):
    __tablename__ = "tasklist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listId: Mapped[str] = mapped_column(String, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    author: Mapped["User"] = relationship(back_populates="tasklist", single_parent=True)

    tasks: Mapped[List["Task"]] = relationship(back_populates="tasklist")


class Task(db.Model):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[int] = mapped_column(String(length=20), nullable=False)
    date_set: Mapped[dt.datetime] = mapped_column(DateTime(), default=dt.datetime.now().replace(microsecond=0))
    date_due: Mapped[dt.datetime] = mapped_column(DateTime())
    # category: Mapped[str] = mapped_column(String) Removed due to limitations, for future extension if we can get sorting/filtering in html working using flask
    notes: Mapped[str] = mapped_column(String)
    complete: Mapped[bool] = mapped_column(Boolean, default=False)

    tasklist_id: Mapped[int] = mapped_column(ForeignKey("tasklist.id"))
    tasklist: Mapped["TaskList"] = relationship(back_populates="tasks")
