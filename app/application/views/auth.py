from flask import Blueprint, app, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.models import TaskList, User, db
from ..objects.forms import Login, Register
from ..objects.helpers import generate_list_id


# Blueprint config
auth = Blueprint(
    "auth", __name__, template_folder="templates", url_prefix="/users"
)

# Create manager instance + user loader
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@auth.route("/register", methods=["GET", "POST"])
def register_user():
    registerform = Register()
    if registerform.validate_on_submit():
        check_exist = db.session.execute(
            db.select(User).where(
                and_(
                    User.email == registerform.email.data,
                    User.username == registerform.username.data,
                )
            )
        )

        if check_exist is None:
            # create new user var
            hashed_password = generate_password_hash(registerform.password.data)
            new_user = User(
                username=registerform.username.data,
                email=registerform.email.data,
                password=hashed_password
            )
            # Retrieve current anonymous tasklist or generate new tasklist 
            tasks = db.session.execute(db.select(TaskList).where(TaskList.listId == request.args.get("tasklist"))).scalar()
            if tasks is None:
                list_id = generate_list_id()
                # Removed retry generate loop for now
                tasks = TaskList(
                    listId=list_id
                )
            tasks.author = new_user
            new_user.tasklist = tasks
            db.session.add(tasks)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("show_list", list_id=tasks.listId))
        else:
            flash("Username or email has already been taken, please try another username or email")
            return render_template("register.html", form=registerform, current_user=current_user)
    elif registerform.errors:
        return render_template("register.html", form=registerform, errors=registerform.errors, current_user=current_user)
    return render_template("register.html", form=registerform, current_user=current_user)


@auth.route("/verify", methods=["GET"])
def verify_user():
    pass


@auth.route("/login", methods=["GET", "POST"])
def login_user():
    loginform = Login()

    if loginform.validate_on_submit():
        retrieved_user = db.session.execute(
            db.select(User).where(User.email == loginform.email.data)
        ).scalar()
        if retrieved_user is None:
            flash("User does not exist, please make a new account")
            return render_template("login.html", form=loginform)
        if check_password_hash(retrieved_user.password, loginform.password.data):
            flash("Email and password do not match")
            return render_template("login.html", form=loginform)
        else:
            login_user(retrieved_user)
            return redirect(url_for("tasklist.show_list", list_id=current_user.tasklist.listId))
    elif loginform.errors:
        return render_template("login.html", errors=loginform.errors, form=loginform)
    return render_template("login.thml", form=loginform)


@auth.route("logout")
def logout_user():
    logout_user()
    return redirect(url_for("tasklist.home_page"))
