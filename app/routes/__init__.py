from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # Register blueprints
    from app.routes.submissions import submissions_bp
    app.register_blueprint(submissions_bp)

    return app
