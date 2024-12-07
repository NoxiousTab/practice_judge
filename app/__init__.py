from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import db
from flask_migrate import Migrate
import os
from .routes.auth import auth
from .routes.submissions import submissions_bp
#app.register_blueprint(auth_blueprint)
login_manager = LoginManager()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
#    exit()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'online_judge.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'tabishsecretkey123456789'
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect unauthorized users to login page

    # Register blueprints
    app.register_blueprint(submissions_bp)
    app.register_blueprint(auth)
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

