"""
Authentication Module using Flask-Login
"""
from flask_login import UserMixin, LoginManager
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class User(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_data: dict):
        self.id = user_data.get('username')
        self.username = user_data.get('username')
        self.email = user_data.get('email', '')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.full_name = user_data.get('full_name', '')
        self.display_name = user_data.get('display_name', '')
        self.department = user_data.get('department', '')
        self.title = user_data.get('title', '')
        self.phone = user_data.get('phone', '')
        self.mobile = user_data.get('mobile', '')
        self.employee_id = user_data.get('employee_id', '')
        self.dn = user_data.get('dn', '')
        self._data = user_data
    
    def get_id(self):
        """Return the username as the unique identifier"""
        return self.username
    
    def to_dict(self):
        """Convert user to dictionary"""
        return self._data
    
    def __repr__(self):
        return f'<User {self.username}>'


class AuthManager:
    """Manages authentication operations"""
    
    def __init__(self, ldap_service):
        self.ldap_service = ldap_service
        self.login_manager = LoginManager()
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'login'
        self.login_manager.login_message = 'Please log in to access this page.'
        self.login_manager.session_protection = 'strong'
        
        @self.login_manager.user_loader
        def load_user(username):
            return self.get_user(username)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with LDAP"""
        try:
            user_data = self.ldap_service.authenticate_user(username, password)
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            logger.error(f"Authentication error: {type(e).__name__}")
            return None
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            user_data = self.ldap_service.get_user_by_username(username)
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {type(e).__name__}")
            return None
