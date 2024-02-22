from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_
from ..objects.helpers import generate_list_id
from ..models.models import Task, TaskList, db
from ..objects.forms import Checkbox, Todo
import datetime as dt

tasklist = Blueprint("tasklist", __name__, template_folder="templates")


# index dud link, redirects to show_list
@tasklist.route("/")
def home_page():
    return redirect(url_for("tasklist.show_list", list_id=generate_list_id()))


# Existing user list
@tasklist.route("/tasks/<list_id>")
def show_list(list_id):
    todoform = Todo()
    checkbox = Checkbox()
    tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId==list_id)).scalar()

    return render_template("index.html", list_id=list_id, form=todoform, checkbox=checkbox, tasks=tasklist, current_user=current_user)


@tasklist.route("/tasks/<list_id>", methods=["POST"])
def add_task(list_id):
    if request.method == "POST":
        todoform = Todo()
        tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId==list_id)).scalar()
        if todoform.validate():
            # Create new task
            new_task = Task(
                name=todoform.name.data,
                date_due=todoform.date_due.data,
                notes=todoform.notes.data
            )

            # If list does not exist in db, create and save
            if tasklist is None:
                tasklist = TaskList(
                    listId=list_id
                )
                db.session.add(tasklist)

            # db relationship linking
            new_task.tasklist = tasklist

            db.session.add(new_task)
            db.session.commit()

            return redirect(url_for("tasklist.show_list", list_id=tasklist.listId))
        else:
            checkbox = Checkbox()
            print(list_id)
            return render_template("index.html", list_id=list_id, form=todoform, checkbox=checkbox, tasks=tasklist, current_user=current_user, errors=todoform.errors)


@tasklist.route("/tasks/<list_id>/<int:task_id>/check", methods=["PATCH"])
def set_task_check(list_id, task_id):
    db.get_or_404(Task, task_id)
    if request.method == "PATCH":
        complete_state = request.get_json()
        tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId == list_id)).scalar()
        task = db.session.execute(db.select(Task).where(and_(Task.tasklist == tasklist,
                                                      Task.id == task_id))).scalar()
        task.complete = complete_state.get("checked")
        db.session.commit()
        return jsonify({"list_id": list_id,
                        "task_id": task_id,
                        "checked": complete_state.get("checked")})


# TODO response on empty string?
# TODO edit task date due
@tasklist.route("/tasks/<list_id>/<int:task_id>/name", methods=["PATCH"])
def edit_task_name(list_id, task_id):
    if request.method == "PATCH":
        tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId == list_id)).scalar()
        task = db.session.execute(db.select(Task).where(and_(Task.tasklist == tasklist,
                                                             Task.id == task_id))).scalar()
        new_name = request.get_json().get("name")
        task.name = new_name
        db.session.commit()
        return jsonify({"name": task.name})


@tasklist.route("/tasks/<list_id>/<int:task_id>/notes", methods=["PATCH"])
def edit_task_notes(list_id, task_id):
    if request.method == "PATCH":
        tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId == list_id)).scalar()
        task = db.session.execute(db.select(Task).where(and_(Task.tasklist == tasklist,
                                                             Task.id == task_id))).scalar()
        new_notes = request.get_json().get("notes")
        task.notes = "" if new_notes == "" else new_notes
        db.session.commit()
        return jsonify({"notes": task.notes})


@tasklist.route("/tasks/<list_id>/<int:task_id>/date-due", methods=["PATCH"])
def edit_task_date_due(list_id, task_id):
    if request.method == "PATCH":
        tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId == list_id)).scalar()
        task = db.session.execute(db.select(Task).where(and_(Task.tasklist == tasklist,
                                                             Task.id == task_id))).scalar()
        new_datetime = dt.datetime.strptime(request.get_json().get("date_due"), "%Y-%m-%dT%H:%M")
        print(new_datetime)
        task.date_due = new_datetime
        db.session.commit()
        return jsonify({"date": task.date_due})


@tasklist.route("/tasks/<list_id>/<int:task_id>")
def delete_task(list_id, task_id):
    selected_task = db.get_or_404(Task, task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return redirect(url_for("tasklist.show_list", list_id=list_id))
