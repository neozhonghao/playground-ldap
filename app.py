"""
Team Dashboard - Simple LDAP-authenticated team directory
"""
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
from models import db, User, StatusMessage, init_db
from ldap_auth import authenticate_ldap, get_all_users_from_ldap
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Create tables
with app.app_context():
    init_db()

@app.route('/')
@login_required
def index():
    """Dashboard home page"""
    # Update last seen
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    
    # Get who's online (active in last 30 minutes)
    online_threshold = datetime.utcnow() - timedelta(minutes=30)
    online_users = User.query.filter(User.last_seen >= online_threshold).all()
    
    # Get current user's status
    status = StatusMessage.query.filter_by(user_id=current_user.id).first()
    
    return render_template('index.html', 
                         online_users=online_users,
                         user_status=status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('login.html')
        
        # Authenticate with LDAP
        user_info = authenticate_ldap(username, password)
        
        if user_info:
            # Check if user exists in database
            user = User.query.filter_by(username=username).first()
            
            if not user:
                # Create new user
                user = User(
                    username=username,
                    email=user_info.get('email', ''),
                    full_name=user_info.get('name', username),
                    department=user_info.get('department', '')
                )
                db.session.add(user)
            else:
                # Update user info
                user.email = user_info.get('email', user.email)
                user.full_name = user_info.get('name', user.full_name)
                user.department = user_info.get('department', user.department)
            
            user.last_seen = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            flash(f'Welcome, {user.full_name}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/directory')
@login_required
def directory():
    """Team directory page"""
    search_query = request.args.get('search', '')
    
    if search_query:
        users = User.query.filter(
            (User.full_name.ilike(f'%{search_query}%')) |
            (User.department.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%'))
        ).all()
    else:
        users = User.query.order_by(User.full_name).all()
    
    return render_template('directory.html', users=users, search_query=search_query)

@app.route('/profile')
@app.route('/profile/<username>')
@login_required
def profile(username=None):
    """User profile page"""
    if username:
        user = User.query.filter_by(username=username).first_or_404()
    else:
        user = current_user
    
    status = StatusMessage.query.filter_by(user_id=user.id).first()
    is_own_profile = (user.id == current_user.id)
    
    return render_template('profile.html', 
                         user=user, 
                         status=status,
                         is_own_profile=is_own_profile)

@app.route('/status', methods=['POST'])
@login_required
def update_status():
    """Update user status message"""
    status_text = request.form.get('status', '').strip()
    
    status = StatusMessage.query.filter_by(user_id=current_user.id).first()
    
    if status_text:
        if not status:
            status = StatusMessage(user_id=current_user.id, message=status_text)
            db.session.add(status)
        else:
            status.message = status_text
            status.updated_at = datetime.utcnow()
        
        flash('Status updated', 'success')
    else:
        if status:
            db.session.delete(status)
        flash('Status cleared', 'info')
    
    db.session.commit()
    return redirect(url_for('profile'))

@app.route('/sync-ldap')
@login_required
def sync_ldap():
    """Admin: Sync all users from LDAP"""
    # TODO: Add admin check
    users_from_ldap = get_all_users_from_ldap()
    
    count = 0
    for user_info in users_from_ldap:
        username = user_info.get('username')
        user = User.query.filter_by(username=username).first()
        
        if not user:
            user = User(
                username=username,
                email=user_info.get('email', ''),
                full_name=user_info.get('name', username),
                department=user_info.get('department', '')
            )
            db.session.add(user)
            count += 1
    
    db.session.commit()
    flash(f'Synced {count} new users from LDAP', 'success')
    return redirect(url_for('directory'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
