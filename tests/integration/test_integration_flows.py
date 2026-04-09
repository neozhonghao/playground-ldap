"""
Integration tests for complete user flows
"""
import pytest
from unittest.mock import patch, Mock


class TestUserFlows:
    """Test complete user workflows"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-key'
        return app.test_client()
    
    def test_complete_login_browse_logout_flow(self, client):
        """Test complete user flow: login -> browse directory -> logout"""
        # Step 1: Login
        with patch('app.auth_manager.authenticate') as mock_auth:
            mock_user = Mock()
            mock_user.username = 'testuser'
            mock_user.full_name = 'Test User'
            mock_auth.return_value = mock_user
            
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
        
        # Step 2: Browse directory
        with patch('app.ldap_service.get_all_users') as mock_users:
            mock_users.return_value = {
                'users': [{'username': 'user1'}, {'username': 'user2'}],
                'total': 2,
                'page': 1,
                'total_pages': 1
            }
            
            response = client.get('/directory')
            assert response.status_code == 200
        
        # Step 3: Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Step 4: Verify can't access protected pages
        response = client.get('/directory')
        assert response.status_code in [302, 401]


class TestErrorRecovery:
    """Test error handling and recovery"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app.test_client()
    
    def test_ldap_server_down_during_login(self, client):
        """Test handling when LDAP server is down"""
        with patch('app.auth_manager.authenticate', side_effect=Exception("LDAP server unavailable")):
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            })
            
            # Should handle gracefully
            assert response.status_code == 200
