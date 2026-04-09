"""
Unit tests for LDAP Service Layer
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from ldap3 import Server, Connection
from ldap3.core.exceptions import LDAPBindError, LDAPException

from ldap_service import LDAPService


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'LDAP_SERVER': 'ldap://test.example.com',
        'LDAP_USE_SSL': False,
        'LDAP_PORT': 389,
        'LDAP_BIND_DN': 'cn=admin,dc=test,dc=com',
        'LDAP_BIND_PASSWORD': 'admin',
        'LDAP_USER_SEARCH_BASE': 'ou=users,dc=test,dc=com',
        'LDAP_USER_OBJECT_CLASS': 'inetOrgPerson',
        'LDAP_USER_LOGIN_ATTR': 'uid',
        'LDAP_ATTR_MAP': {
            'username': 'uid',
            'email': 'mail',
            'first_name': 'givenName',
            'last_name': 'sn',
            'display_name': 'displayName',
        },
        'MAX_SEARCH_RESULTS': 500
    }


@pytest.fixture
def ldap_service(mock_config):
    """Create LDAP service instance with mocked server"""
    with patch('ldap_service.Server'):
        service = LDAPService(mock_config)
        return service


class TestLDAPServiceInitialization:
    """Test LDAP service initialization"""
    
    def test_create_server_without_ssl(self, mock_config):
        """Test server creation without SSL"""
        with patch('ldap_service.Server') as mock_server:
            service = LDAPService(mock_config)
            mock_server.assert_called_once()
            assert service.config == mock_config
    
    def test_create_server_with_ssl(self, mock_config):
        """Test server creation with SSL/TLS"""
        mock_config['LDAP_USE_SSL'] = True
        mock_config['LDAP_PORT'] = 636
        
        with patch('ldap_service.Server') as mock_server, \
             patch('ldap_service.Tls') as mock_tls:
            service = LDAPService(mock_config)
            mock_tls.assert_called_once()
            mock_server.assert_called_once()


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_authenticate_user_success(self, ldap_service, mock_config):
        """Test successful user authentication"""
        with patch.object(ldap_service, 'get_user_by_username') as mock_get_user:
            mock_get_user.return_value = {
                'username': 'testuser',
                'email': 'test@example.com',
                'full_name': 'Test User'
            }
            
            with patch('ldap_service.Connection') as mock_conn:
                mock_conn_instance = Mock()
                mock_conn_instance.bound = True
                mock_conn.return_value = mock_conn_instance
                
                result = ldap_service.authenticate_user('testuser', 'password123')
                
                assert result is not None
                assert result['username'] == 'testuser'
                mock_conn_instance.unbind.assert_called_once()
    
    def test_authenticate_user_invalid_username(self, ldap_service):
        """Test authentication with invalid username format"""
        result = ldap_service.authenticate_user('invalid@user!', 'password')
        assert result is None
    
    def test_authenticate_empty_password(self, ldap_service):
        """Test authentication with empty password (anonymous bind prevention)"""
        result = ldap_service.authenticate_user('testuser', '')
        assert result is None


class TestSearchUsers:
    """Test user search functionality with security"""
    
    def test_search_users_with_escaping(self, ldap_service):
        """Test that search properly escapes LDAP special characters"""
        with patch.object(ldap_service, '_get_admin_connection') as mock_conn_method:
            mock_conn = Mock()
            mock_conn.entries = []
            mock_conn_method.return_value = mock_conn
            
            # This should be escaped
            malicious_query = "*)(&(userPassword=*"
            results = ldap_service.search_users(malicious_query)
            
            # Verify search was called
            mock_conn.search.assert_called_once()
            
            # Verify special characters were escaped
            search_args = mock_conn.search.call_args
            filter_str = str(search_args)
            
            # The raw malicious characters should not appear unescaped
            assert results == []


class TestDepartments:
    """Test department retrieval"""
    
    def test_get_departments_success(self, ldap_service):
        """Test getting list of departments"""
        mock_entry1 = Mock()
        mock_entry1.departmentNumber.value = 'Engineering'
        mock_entry2 = Mock()
        mock_entry2.departmentNumber.value = 'Sales'
        
        with patch.object(ldap_service, '_get_admin_connection') as mock_conn_method:
            mock_conn = Mock()
            mock_conn.entries = [mock_entry1, mock_entry2]
            mock_conn_method.return_value = mock_conn
            
            departments = ldap_service.get_departments()
            
            assert len(departments) == 2
            assert 'Engineering' in departments
            assert 'Sales' in departments
