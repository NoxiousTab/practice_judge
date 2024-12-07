from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  # Get the email from the form
        
        if not username or not password or not email:
            flash('Please fill out all fields.')
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Username already exists. Please choose another.')
            return redirect(url_for('auth.register'))
        if(existing_email):
            flash('Email is already in use. Please choose another')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(password)
        
        # Create new user with email
        new_user = User(username=username, password=hashed_password, email=email, email_confirmed_at=datetime.utcnow())
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("hit")
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # Set session for user_id
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('submissions.dashboard'))  # Redirect to dashboard
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
    return render_template('login.html')


@auth.route('/logout')
def logout():
    # Clear the user session
    session.pop('user_id', None)
    session.clear()  # Optionally clear the entire session if other data is stored
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))  # Redirect to the login page
