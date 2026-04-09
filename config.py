"""
Configuration Management for LDAP Employee Directory
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # LDAP Configuration
    LDAP_SERVER = os.getenv('LDAP_SERVER', 'ldap://localhost')
    LDAP_USE_SSL = os.getenv('LDAP_USE_SSL', 'False').lower() == 'true'
    LDAP_PORT = int(os.getenv('LDAP_PORT', '636' if LDAP_USE_SSL else '389'))
    
    # LDAP Bind Credentials (for search operations)
    LDAP_BIND_DN = os.getenv('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
    LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD', 'admin')
    
    # LDAP Search Configuration
    LDAP_BASE_DN = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')
    LDAP_USER_SEARCH_BASE = os.getenv('LDAP_USER_SEARCH_BASE', 'ou=users,dc=example,dc=com')
    LDAP_USER_OBJECT_CLASS = os.getenv('LDAP_USER_OBJECT_CLASS', 'inetOrgPerson')
    LDAP_USER_LOGIN_ATTR = os.getenv('LDAP_USER_LOGIN_ATTR', 'uid')
    
    # LDAP Attribute Mapping
    LDAP_ATTR_MAP = {
        'username': 'uid',
        'email': 'mail',
        'first_name': 'givenName',
        'last_name': 'sn',
        'display_name': 'displayName',
        'department': 'departmentNumber',
        'title': 'title',
        'phone': 'telephoneNumber',
        'mobile': 'mobile',
        'employee_id': 'employeeNumber',
        'manager': 'manager',
        'photo': 'jpegPhoto'
    }
    
    # Application Settings
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 50))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 500))
    ENABLE_AUDIT_LOG = os.getenv('ENABLE_AUDIT_LOG', 'True').lower() == 'true'
    
    # Security Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LDAP_USE_SSL = False
    SESSION_COOKIE_SECURE = False
    # Use filesystem sessions for development (no Redis required)
    SESSION_TYPE = 'filesystem'
    # Use in-memory rate limiting for development (no Redis required)
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Ensure SSL in production
    LDAP_USE_SSL = True
    WTF_CSRF_ENABLED = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
