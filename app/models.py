from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)  # Programming language
    verdict = db.Column(db.String(50), nullable=False)   # Verdict (e.g., Accepted, Wrong Answer)
    test_cases = db.Column(db.Integer, nullable=False)   # Number of test cases
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define the relationship to the User model
    user = relationship('User', backref='submissions')

    def __repr__(self):
        return f'<Submission {self.id}, {self.title}>'



class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


