"""
Integration tests for Flask application
"""
import pytest
from unittest.mock import Mock, patch
from flask import session
from app import app as flask_app


@pytest.fixture
def app():
    """Create Flask application for testing"""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    return flask_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAuthenticationRoutes:
    """Test authentication routes"""
    
    def test_login_page_get(self, client):
        """Test GET login page"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        })
        
        assert b'provide both username and password' in response.data.lower()


class TestProtectedRoutes:
    """Test protected routes require authentication"""
    
    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]  # Redirect to login
    
    def test_directory_requires_auth(self, client):
        """Test directory requires authentication"""
        response = client.get('/directory')
        assert response.status_code in [302, 401]


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_check_public(self, client):
        """Test health check endpoint is public"""
        with patch('app.ldap_service.test_connection', return_value=True):
            response = client.get('/api/health')
            assert response.status_code == 200
            data = response.get_json()
            assert 'status' in data
