import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from models import User
from forms import LoginForm, RegistrationForm

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def create_admin_user():
    """Create admin user if it doesn't exist"""
    admin_username = current_app.config['ADMIN_USERNAME']
    admin_email = current_app.config['ADMIN_EMAIL']
    admin_password = current_app.config['ADMIN_PASSWORD']
    
    # Check if admin user exists
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        logger.info(f"Creating admin user: {admin_username}")
        admin = User(username=admin_username, email=admin_email, is_admin=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created successfully")
    else:
        logger.info("Admin user already exists")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('boards.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        flash(f'Welcome back, {user.username}!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('boards.index')
        
        return redirect(next_page)
    
    return render_template('login.html', form=form, title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('boards.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if email exists
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email already registered. Please use a different one.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form, title='Register')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('boards.index'))
