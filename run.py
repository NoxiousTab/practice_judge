from flask import Flask
from app import create_app
from app.models import db
from app.routes.auth import auth
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
'''app = Flask(__name__, template_folder="app/templates")
app.secret_key = 'your_secret_key'

#app.add_url_rule('/register', view_func=register)
#app.add_url_rule('/login', view_func=login)'''
app = create_app()
with app.app_context():
	db.create_all()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
