from flask import app
from .models.models import db
from .views.auth import login_manager

def init_app():
    db.init_app(app)


    with app.create_context():
        db.create_all()
    return app