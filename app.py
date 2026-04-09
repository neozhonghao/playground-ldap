"""
Enterprise Employee Directory & Authentication System
Main Flask Application with Security Fixes Applied
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime
import os

from config import config
from ldap_service import LDAPService
from auth import AuthManager, User
from ldap_utils import validate_page_number

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
Session(app)
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
)

# Initialize services
ldap_service = LDAPService(app.config)
auth_manager = AuthManager(ldap_service)
auth_manager.init_app(app)


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Rate limit login attempts
def login():
    """Login page and handler with security fixes"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Input validation
        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('login.html')
        
        # Validate username length
        if len(username) > 64:
            flash('Invalid username', 'error')
            return render_template('login.html')
        
        # Authenticate user
        user = auth_manager.authenticate(username, password)
        
        if user:
            login_user(user, remember=remember)
            
            # Log successful login (without password!)
            logger.info(f"User logged in: {username}")
            
            # Audit log if enabled
            if app.config.get('ENABLE_AUDIT_LOG'):
                logger.info(f"AUDIT: Login successful - User: {username}, IP: {request.remote_addr}")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f"Failed login attempt: {username}, IP: {request.remote_addr}")
            
            # Audit log if enabled
            if app.config.get('ENABLE_AUDIT_LOG'):
                logger.warning(f"AUDIT: Login failed - User: {username}, IP: {request.remote_addr}")
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout handler"""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    
    # Audit log if enabled
    if app.config.get('ENABLE_AUDIT_LOG'):
        logger.info(f"AUDIT: Logout - User: {username}")
    
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))


# ============================================================================
# MAIN APPLICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - redirects to dashboard or login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get recent statistics
    try:
        user_stats = ldap_service.get_all_users(page=1, per_page=1)
        total_employees = user_stats.get('total', 0)
        
        departments = ldap_service.get_departments()
        total_departments = len(departments)
        
    except Exception as e:
        logger.error(f"Error loading dashboard stats: {type(e).__name__}")
        total_employees = 0
        total_departments = 0
    
    return render_template(
        'dashboard.html',
        total_employees=total_employees,
        total_departments=total_departments,
        current_time=datetime.now()
    )


@app.route('/directory')
@login_required
def directory():
    """Employee directory with pagination"""
    # Validate and sanitize page number
    page = validate_page_number(request.args.get('page', 1))
    per_page = app.config['ITEMS_PER_PAGE']
    
    try:
        result = ldap_service.get_all_users(page=page, per_page=per_page)
        users = result['users']
        total = result['total']
        total_pages = result['total_pages']
        
    except Exception as e:
        logger.error(f"Error loading directory: {type(e).__name__}")
        users = []
        total = 0
        total_pages = 1
        flash('Error loading employee directory', 'error')
    
    return render_template(
        'directory.html',
        users=users,
        page=page,
        total=total,
        total_pages=total_pages
    )


@app.route('/search')
@login_required
@limiter.limit("30 per minute")  # Rate limit search
def search():
    """Search employees with input validation"""
    query = request.form.get('q', '').strip() if request.method == 'POST' else request.args.get('q', '').strip()
    department = request.args.get('department', '')
    
    # Limit query length
    if query and len(query) > 100:
        flash('Search query too long', 'error')
        return render_template('search.html', users=[], query='')
    
    if not query and not department:
        return render_template('search.html', users=[], query='')
    
    # Build filters
    filters = {}
    if department:
        filters['department'] = department
    
    try:
        users = ldap_service.search_users(query, filters)
        logger.info(f"Search query returned {len(users)} results")
        
        # Audit log if enabled
        if app.config.get('ENABLE_AUDIT_LOG'):
            logger.info(f"AUDIT: Search - User: {current_user.username}, Query: {query[:50]}, Results: {len(users)}")
            
    except Exception as e:
        logger.error(f"Error searching users: {type(e).__name__}")
        users = []
        flash('Error performing search', 'error')
    
    return render_template(
        'search.html',
        users=users,
        query=query,
        department=department
    )


@app.route('/profile/<username>')
@login_required
def profile(username):
    """View employee profile with input validation"""
    # Basic username validation
    if not username or len(username) > 64:
        flash('Invalid username', 'error')
        return redirect(url_for('directory'))
    
    try:
        user_data = ldap_service.get_user_by_username(username)
        
        if not user_data:
            flash('User not found', 'error')
            return redirect(url_for('directory'))
        
        # Check if viewing own profile
        is_own_profile = (current_user.username == username)
        
        # Audit log if enabled
        if app.config.get('ENABLE_AUDIT_LOG'):
            logger.info(f"AUDIT: Profile view - Viewer: {current_user.username}, Profile: {username}")
        
    except Exception as e:
        logger.error(f"Error loading profile for {username}: {type(e).__name__}")
        flash('Error loading profile', 'error')
        return redirect(url_for('directory'))
    
    return render_template(
        'profile.html',
        user=user_data,
        is_own_profile=is_own_profile
    )


@app.route('/profile')
@login_required
def my_profile():
    """View own profile"""
    return redirect(url_for('profile', username=current_user.username))


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/departments')
@login_required
def api_departments():
    """API endpoint to get all departments"""
    try:
        departments = ldap_service.get_departments()
        return jsonify({'departments': departments})
    except Exception as e:
        logger.error(f"Error fetching departments: {type(e).__name__}")
        return jsonify({'error': 'Failed to fetch departments'}), 500


@app.route('/api/search')
@login_required
@limiter.limit("30 per minute")
def api_search():
    """API endpoint for autocomplete search with input validation"""
    query = request.args.get('q', '').strip()
    
    # Validate query length
    if len(query) < 2:
        return jsonify({'results': []})
    
    if len(query) > 100:
        return jsonify({'error': 'Query too long'}), 400
    
    try:
        users = ldap_service.search_users(query)
        # Limit to 10 results for autocomplete
        results = [
            {
                'username': user.get('username', ''),
                'full_name': user.get('full_name', ''),
                'email': user.get('email', ''),
                'department': user.get('department', ''),
                'title': user.get('title', '')
            }
            for user in users[:10]
        ]
        return jsonify({'results': results})
    except Exception as e:
        logger.error(f"Error in API search: {type(e).__name__}")
        return jsonify({'error': 'Search failed'}), 500


@app.route('/api/health')
@csrf.exempt  # Health check endpoint doesn't need CSRF
def health_check():
    """Health check endpoint"""
    ldap_healthy = ldap_service.test_connection()
    
    return jsonify({
        'status': 'healthy' if ldap_healthy else 'unhealthy',
        'ldap_connection': ldap_healthy,
        'timestamp': datetime.now().isoformat()
    }), 200 if ldap_healthy else 503


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {type(error).__name__}")
    # Don't expose error details to user
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('403.html'), 403


@app.errorhandler(429)
def ratelimit_error(error):
    """Handle rate limit errors"""
    return render_template('429.html'), 429


# ============================================================================
# TEMPLATE FILTERS
# ============================================================================

@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime for display"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    # Test LDAP connection on startup
    if ldap_service.test_connection():
        logger.info("✓ LDAP connection successful")
    else:
        logger.warning("✗ LDAP connection failed - check configuration")
    
    # Run application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
