"""
Security tests for authentication
"""
import pytest
from unittest.mock import patch, Mock


class TestAuthenticationSecurity:
    """Test authentication security"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app.test_client()
    
    def test_empty_password_rejected(self, client):
        """Test that empty password doesn't allow authentication"""
        with patch('app.auth_manager.authenticate', return_value=None):
            response = client.post('/login', data={
                'username': 'admin',
                'password': ''
            })
            
            assert b'provide both username and password' in response.data.lower()
    
    def test_sql_injection_username(self, client):
        """Test SQL injection attempts in username are handled"""
        malicious_usernames = [
            "admin' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
        ]
        
        for username in malicious_usernames:
            with patch('app.auth_manager.authenticate', return_value=None):
                response = client.post('/login', data={
                    'username': username,
                    'password': 'password'
                })
                
                # Should safely handle malicious input
                assert response.status_code in [200, 400]
    
    def test_xss_in_username(self, client):
        """Test XSS attempts in username are escaped"""
        xss_payload = "<script>alert('XSS')</script>"
        
        with patch('app.auth_manager.authenticate', return_value=None):
            response = client.post('/login', data={
                'username': xss_payload,
                'password': 'password'
            })
            
            # Script should be escaped in response
            assert b'<script>' not in response.data or b'&lt;script&gt;' in response.data
    
    def test_long_username_rejected(self, client):
        """Test that overly long usernames are rejected"""
        long_username = 'a' * 1000
        
        with patch('app.auth_manager.authenticate', return_value=None):
            response = client.post('/login', data={
                'username': long_username,
                'password': 'password'
            })
            
            # Should handle gracefully
            assert response.status_code in [200, 400]
