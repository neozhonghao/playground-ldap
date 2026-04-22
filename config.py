"""
Configuration for Team Dashboard
"""
import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///team_dashboard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # LDAP Configuration
    LDAP_SERVER = os.environ.get('LDAP_SERVER', 'ldap://localhost')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', 389))
    LDAP_USE_SSL = os.environ.get('LDAP_USE_SSL', 'False').lower() == 'true'
    LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'cn=admin,dc=example,dc=com')
    LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD', '')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=example,dc=com')
    LDAP_USER_SEARCH_BASE = os.environ.get('LDAP_USER_SEARCH_BASE', 'ou=users,dc=example,dc=com')
    LDAP_USER_OBJECT_CLASS = os.environ.get('LDAP_USER_OBJECT_CLASS', 'inetOrgPerson')
    LDAP_USER_LOGIN_ATTR = os.environ.get('LDAP_USER_LOGIN_ATTR', 'uid')
