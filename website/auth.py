from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from .models import User, db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

def is_password_strong(password):
    """Check if password meets strength requirements"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # At least one uppercase
        return False
    if not re.search(r'[a-z]', password):  # At least one lowercase
        return False
    if not re.search(r'\d', password):     # At least one digit
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # At least one special character
        return False
    return True

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if check_password_hash(user.password, password):
                logger.info(f"User {username} logged in successfully")
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                logger.warning(f"Failed login attempt for {username}: incorrect password")
                flash("Incorrect password, please try again.", category="error")
        else:
            logger.warning(f"Failed login attempt: username {username} does not exist")
            flash("Username does not exist!", category="error")
    
    return render_template("login.html", user=current_user)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        dob_str = request.form.get('dob').strip()
        
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", category="error")
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(username=email).first()
        
        if user and user.DOB == dob:
            session['reset_user_id'] = user.id
            session['reset_expires'] = (datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()
            logger.info(f"Password reset initiated for user ID: {user.id}")
            
            flash("Your identity has been verified. Please set a new password.", category="success")
            return redirect(url_for('auth.reset_password'))
        else:
            logger.warning(f"Failed password reset attempt for email: {email}")
            flash("If your email exists in our system and your information matches, you'll be able to reset your password.", category="info")
            import time
            time.sleep(1)
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # Check if reset session exists and is not expired
    user_id = session.get('reset_user_id')
    reset_expires = session.get('reset_expires')
    
    if not user_id or not reset_expires:
        flash("Session expired or unauthorized access.", category="error")
        return redirect(url_for('auth.login'))
    
    # Check if reset session is expired (15 minutes)
    if datetime.now(timezone.utc).timestamp() > reset_expires:
        session.pop('reset_user_id', None)
        session.pop('reset_expires', None)
        flash("Reset session expired. Please request a new password reset.", category="error")
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.get(user_id)
    if not user:
        session.pop('reset_user_id', None)
        session.pop('reset_expires', None)
        flash("User not found. Please contact support.", category="error")
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash("Passwords do not match.", category="error")
            return render_template('reset_password.html')
        
        # Validate password strength
        if not is_password_strong(new_password):
            flash("Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.", category="error")
            return render_template('reset_password.html')
        
        try:
            # Update password
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            
            # Clear session data
            session.pop('reset_user_id', None)
            session.pop('reset_expires', None)
            
            logger.info(f"Password reset successful for user ID: {user_id}")
            flash("Password reset successfully! Please login.", category="success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password reset failed for user ID: {user_id}. Error: {str(e)}")
            flash("An error occurred while resetting your password. Please try again.", category="error")
            return render_template('reset_password.html')
    
    return render_template('reset_password.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email').strip()  # Remove whitespace
        first_name = request.form.get('firstName').strip()
        last_name = request.form.get('lastName').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        dob_str = request.form.get('dob').strip()
        user_type = request.form.get('user_type')
        student_level = request.form.get('student_level')
        
        # Validate all required fields
        if not email or not first_name or not last_name or not password or not confirm_password or not dob_str or not user_type:
            flash('All fields are required.', category='error')
            return render_template("signup.html", user=current_user)
        
        # Check if user already exists
        user = User.query.filter_by(username=email).first()
        if user:
            flash('Email already exists.', category='error')
            return render_template("signup.html", user=current_user)
        
        # Validate password match
        if password != confirm_password:
            flash('Passwords don\'t match.', category='error')
            return render_template("signup.html", user=current_user)
        
        # Validate password strength
        if not is_password_strong(password):
            flash("Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.", category="error")
            return render_template("signup.html", user=current_user)
        
        # Convert the date string to a Python date object
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', category='error')
            return render_template("signup.html", user=current_user)
        
        try:
            # Create new user
            new_user = User(
                username=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                DOB=dob,
                user_type=user_type,
                student_level=student_level
            )
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"New user created: {email}")
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create user {email}. Error: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', category='error')
            return render_template("signup.html", user=current_user)
    
    return render_template("signup.html", user=current_user)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def edit_details():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        first_name = request.form.get('firstName').strip()
        last_name = request.form.get('lastName').strip()
        dob_str = request.form.get('dob').strip()
        password = request.form.get('password')
        
        # Get current user
        user = current_user
        
        # Check if email is being changed and if it's already in use
        if email != user.username:
            existing_user = User.query.filter_by(username=email).first()
            if existing_user:
                flash('Email already exists.', category='error')
                return render_template("settings.html", user=current_user)
        
        try:
            # Update user details
            user.username = email
            user.first_name = first_name
            user.last_name = last_name
            
            # Convert DOB if provided
            if dob_str:
                try:
                    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    user.DOB = dob
                except ValueError:
                    flash('Invalid date format. Please use YYYY-MM-DD.', category='error')
                    return render_template("settings.html", user=current_user)
            
            # Update password if provided
            if password:
                if not is_password_strong(password):
                    flash("Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.", category="error")
                    return render_template("settings.html", user=current_user)
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
            
            db.session.commit()
            logger.info(f"User details updated for user ID: {user.id}")
            flash("Details updated successfully!", category="success")
            return redirect(url_for('views.home'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update details for user ID: {user.id}. Error: {str(e)}")
            flash("An error occurred while updating your details. Please try again.", category="error")
            return render_template("settings.html", user=current_user)
    
    return render_template("settings.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    return redirect(url_for('auth.login'))