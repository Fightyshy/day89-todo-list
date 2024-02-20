from flask import Flask, app
from flask_bootstrap import Bootstrap5
from .models.models import db
from .views.auth import login_manager


def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"  # csrf
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"

    bs5 = Bootstrap5()
    bs5.init_app(app)

    db.init_app(app)

    from .views.tasklist import tasklist
    from .views.auth import auth
    app.register_blueprint(tasklist)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()
    return app
