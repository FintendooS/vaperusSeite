import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = '/var/www/vapeApp/uploads/'
#UPLOAD_FOLDER = 'C:/Users/Finlay/PycharmProjects/vapeApp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'mov'}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'DimaIstSchwul123'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    from .models import User

    if not path.exists("instance/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Database created!")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


app = create_app()
