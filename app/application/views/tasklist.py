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

# @tasklist.route("/tasks", methods=["POST"])
# def add_task():
#     if request.method == "POST":
#         # Validate add task request and turn into a new Task object
#         form = Todo()
#         if form.validate():
#             new_task = Task(
#                 name=form.name.data,
#                 date_due=dt.datetime.strptime(request.form["date_due"], "%Y-%m-%dT%H:%M"),
#                 notes=form.notes.data
#             )

#             # Retrieve tasklist or create current one
#             prev_link = request.referrer.split("/")
#             # Check 4th element (list_id expected location)
#             if prev_link[-1] != "":
#                 tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId == prev_link[-1])).scalar()
#             elif prev_link[-1] == "":
#                 # Create new list but do not link to author, is now anonymous list
#                 tasklist = TaskList(
#                     listId=generate_list_id(),
#                     author=None
#                 )
#                 db.session.add(tasklist)
#             new_task.tasklist = tasklist
#             db.session.add(new_task)
#             db.session.commit()

#             return redirect(url_for("tasklist.show_list", list_id=tasklist.listId))
#         else:
#             prev_link = request.referrer.split("/")
#             print(prev_link)
#             tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId == prev_link[-1])).scalar()
#             checkbox = Checkbox()
#             return redirect(f"/tasks/{prev_link[-1]}")
#             # return redirect(url_for("tasklist.show_list", list_id=prev_link[-1], errors=form.errors))
#             # return redirect('index.html', form=form, checkbox=checkbox, tasks=tasklist, current_user=current_user, errors=form.errors)

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


# TODO fix
@tasklist.route("/task/<int:task_id>")
def delete_task(task_id):
    selected_task = db.get_or_404(Task, task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return redirect(url_for("show_list", list_id=request.args.get("list_id")))
