import random
import string
from typing import List
from flask import *
from flask_bootstrap import Bootstrap5
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import AnonymousUserMixin, UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt

# inits
app = Flask(__name__)

# config
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b" #csrf
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
Bootstrap5(app)
db = SQLAlchemy()

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# flask-login
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Models
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
    date_set: Mapped[dt.datetime] = mapped_column(Date(), default=dt.datetime.now().date())# TODO fully adapt for Date ONLY
    date_due: Mapped[dt.datetime] = mapped_column(Date())
    # category: Mapped[str] = mapped_column(String) Removed due to limitations, for future extension if we can get sorting/filtering in html working using flask
    notes: Mapped[str] = mapped_column(String)
    complete: Mapped[bool] = mapped_column(Boolean)

    tasklist_id: Mapped[int] = mapped_column(ForeignKey("tasklist.id"))
    tasklist: Mapped["TaskList"] = relationship(back_populates="tasks")

with app.app_context():
    db.create_all()


def generate_list_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# endpoints
# Brand new page
@app.route("/", methods=["GET", "POST"])
def home_page():
    todoform = Todo()
    checkbox = Checkbox()

    return render_template("index.html", form=todoform, checkbox=checkbox, current_user=current_user, tasks=None)
# Existing list
@app.route("/<list_id>", methods=["GET", "POST"])
def show_list(list_id):
    todoform = Todo()
    checkbox = Checkbox()
    tasklist = db.session.execute(db.select(TaskList).where(TaskList.listId==list_id)).scalar()

    if request.method=="POST":
        check = True if request.form["checked"]=="true" else False
        selected_task = db.get_or_404(Task, request.form["taskid"])
        selected_task.complete = True if check else False
        db.session.commit()

    return render_template("index.html", form=todoform, checkbox=checkbox, tasks=tasklist, current_user=current_user)

# NOT AJAX
@app.route("/task", methods=["POST"])
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

# TODO AJAX handling - convert to form.
@app.route("/task/<int:task_id>", methods=["POST"])
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

# TODO AJAX handling
@app.route("/task/<int:task_id>")
def delete_task(task_id):
    selected_task = db.get_or_404(Task, task_id)
    db.session.delete(selected_task)
    db.session.commit()
    return redirect(url_for("show_list", list_id=request.args.get("list_id")))

@app.route("/item")
def test():
    print("test")
# @app.route("/add-category", methods=["GET", "POST"])
# def add_category():
#     pass

@app.route("/register", methods=["GET", "POST"])
def register():
    registerform = Register()
    if registerform.validate_on_submit():
        if db.session.execute(db.select(User).where(User.username==registerform.username.data)).scalar() is not None:
            flash("Username already exists")
            return redirect((url_for("register")))
        if db.session.execute(db.select(User).where(User.email==registerform.email.data)).scalar() is not None:
            flash("User email already exists")
            return redirect((url_for("register")))
        if registerform.password.data == registerform.repeat_pw.data:
            hashed_pw = generate_password_hash(registerform.password.data)
            tasks = db.session.execute(db.select(TaskList).where(TaskList.listId==request.args.get("tasklist"))).scalar()
            if tasks is not None:
                new_user = User(
                    username = registerform.username.data,
                    email = registerform.email.data,
                    password = hashed_pw,
                    tasklist = tasks
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('show_list', list_id=tasks.listId))
            else:
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

                new_user = User(
                    username = registerform.username.data,
                    email = registerform.email.data,
                    password = hashed_pw,
                    tasklist = new_tasklist
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('show_list', list_id=new_tasklist.listId))
        else:
            pass
    return render_template("register.html", form=registerform, current_user=current_user)

@app.route("/login", methods=["GET","POST"])
def login():
    loginform = Login()
    if loginform.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == loginform.email.data))
        user = result.scalar()
        if not user:
            flash("User does not exist, please make a new account")
            return redirect(url_for("login"))
        if not check_password_hash(user.password, loginform.password.data):
            flash("Wrong password")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("show_list", list_id=current_user.tasklist.listId))
    return render_template("login.html", form=loginform, current_user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home_page"))

if __name__ == "__main__":
    app.run(debug=True)