from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from ..objects.helpers import generate_list_id
from ..models.models import Task, TaskList, db
from ..objects.forms import Checkbox, Todo
import datetime as dt

tasklist = Blueprint("tasklist", __name__, template_folder="templates")

# Anonymous list
@tasklist.route("/")
def home_page():
    todoform = Todo()
    checkbox = Checkbox()

    return render_template("index.html", form=todoform, checkbox=checkbox, current_user=current_user, tasks=None)


# Existing user list
@login_required
@tasklist.route("/tasks/<list_id>", methods=["GET", "POST"])
def show_list(list_id):
    todoform = Todo()
    checkbox = Checkbox()
    tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId==list_id)).scalar()

    if request.method == "POST":
        check = True if request.form["checked"]=="true" else False
        selected_task = db.get_or_404(Task, request.form["taskid"])
        selected_task.complete = True if check else False
        db.session.commit()

    return render_template("index.html", form=todoform, checkbox=checkbox, tasks=tasklist, current_user=current_user)


@tasklist.route("/tasks", methods=["POST"])
def add_task():
    if request.method=="POST":
        # referrer is the previous url
        # check if it was home or show_list
        # if from home, make new list_id, commit new tasklist
        prev_link = request.referrer
        new_tasklist = None
        if prev_link=="http://localhost:5000/":
            list_id = generate_list_id()
            while True:
                if db.session.execute(db.select(TaskList).where(TaskList.listId==list_id)).scalar() is not None:
                    list_id = generate_list_id()
                else:
                    break
            new_tasklist = TaskList(
                listId=generate_list_id(),
                author=None
            )

            db.session.add(new_tasklist)
            db.session.commit()

        # get list id
        selected_id=prev_link[22:]
        if len(selected_id)==8:
            selected_list = db.session.execute(db.select(TaskList).where(TaskList.listId==selected_id)).scalar()
        else:
            selected_list = new_tasklist

        new_task = Task(
            name=request.form["name"],
            date_due=dt.datetime.strptime(request.form["date_due"], "%Y-%m-%d").date(),
            notes=request.form["notes"],
            complete=False,
            tasklist=selected_list
        )
        db.session.add(new_task)
        db.session.commit()
        print("added successfully")
        return redirect(url_for("show_list", list_id=selected_list.listId))

@tasklist.route("/task/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    db.get_or_404(Task, task_id)
    if request.method=="POST":
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
            "name":to_edit.name,
            "notes": to_edit.notes,
            "datedue": to_edit.date_due
        })
    return ""

@tasklist.route("/task/<int:task_id>")
def delete_task(task_id):
    selected_task = db.get_or_404(Task, task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return redirect(url_for("show_list", list_id=request.args.get("list_id")))
