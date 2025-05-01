from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import db
from models.user import User
from models.wallet import Wallet

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            hashed_password=hashed_password
        )

        try:
            # Add the user first to get an ID
            db.session.add(new_user)
            db.session.flush()  # This assigns the ID without committing
            
            # Create a wallet for the new user with 5 tokens (instead of 0)
            new_wallet = Wallet(user_id=new_user.id, balance=5)
            db.session.add(new_wallet)
            
            # Now commit both operations
            db.session.commit()
            
            flash('Registration successful! 5 tokens have been added to your account. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('auth/login.html')
            
        # Check if the user has check_password method or use werkzeug directly
        if hasattr(user, 'check_password') and callable(getattr(user, 'check_password')):
            password_correct = user.check_password(password)
        else:
            password_correct = check_password_hash(user.hashed_password, password)
            
        if not password_correct:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('auth/login.html')
            
        login_user(user, remember=remember)
        
        # Check if user has a wallet, create one if not
        wallet = Wallet.query.filter_by(user_id=user.id).first()
        if not wallet:
            new_wallet = Wallet(user_id=user.id, balance=5)
            db.session.add(new_wallet)
            db.session.commit()
            flash('A wallet has been created for you with 5 free tokens!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.home'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    # Here you would implement password reset request logic
    # This is just a placeholder template rendering
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In a real app, you'd send an email here
            flash('Check your email for instructions to reset your password.', 'info')
        else:
            flash('No account found with that email.', 'warning')
        
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_request.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    # Here you would validate the token and let the user set a new password
    # This is just a placeholder
    if request.method == 'POST':
        flash('Your password has been updated.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html')

@auth_bp.route('/account-verification/<token>')
def verify_account(token):
    # This would verify a user's email
    # Just a placeholder
    flash('Your account has been verified.', 'success')
    return redirect(url_for('auth.login'))