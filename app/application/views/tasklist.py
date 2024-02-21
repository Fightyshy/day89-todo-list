from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
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


# TODO fix
@tasklist.route("/task/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    db.get_or_404(Task, task_id)
    if request.method == "POST":
        print(request.form["name"])
        to_edit = db.get_or_404(Task, request.form["id"])
        to_edit.name = request.form["name"]
        to_edit.notes = request.form["notes"]
        to_edit.date_due = dt.datetime.strptime(request.form["datedue"], "%Y-%m-%d").date()
        db.session.commit()
        print("Successful recieved")
        # Respond to ajax request
        # Ensure .done overrides once saved
        return jsonify({
            "name": to_edit.name,
            "notes": to_edit.notes,
            "datedue": to_edit.date_due
        })
    return ""


@tasklist.route("/tasks/<list_id>/<int:task_id>")
def delete_task(list_id, task_id):
    selected_task = db.get_or_404(Task, task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return redirect(url_for("tasklist.show_list", list_id=list_id))
