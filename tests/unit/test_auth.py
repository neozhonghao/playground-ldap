"""
Unit tests for Authentication Module
"""
import pytest
from unittest.mock import Mock, patch
from auth import User, AuthManager


class TestUserClass:
    """Test User class"""
    
    def test_user_initialization(self):
        """Test user object creation"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'full_name': 'Test User',
            'department': 'Engineering'
        }
        
        user = User(user_data)
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.full_name == 'Test User'
        assert user.department == 'Engineering'
    
    def test_user_get_id(self):
        """Test get_id method"""
        user = User({'username': 'testuser'})
        assert user.get_id() == 'testuser'
    
    def test_user_missing_fields(self):
        """Test user with missing optional fields"""
        user = User({'username': 'testuser'})
        
        assert user.username == 'testuser'
        assert user.email == ''
        assert user.department == ''


class TestAuthManager:
    """Test AuthManager class"""
    
    @pytest.fixture
    def mock_ldap_service(self):
        """Mock LDAP service"""
        return Mock()
    
    @pytest.fixture
    def auth_manager(self, mock_ldap_service):
        """Create auth manager with mocked LDAP service"""
        return AuthManager(mock_ldap_service)
    
    def test_authenticate_success(self, auth_manager, mock_ldap_service):
        """Test successful authentication"""
        user_data = {'username': 'testuser', 'email': 'test@example.com'}
        mock_ldap_service.authenticate_user.return_value = user_data
        
        user = auth_manager.authenticate('testuser', 'password123')
        
        assert user is not None
        assert isinstance(user, User)
        assert user.username == 'testuser'
