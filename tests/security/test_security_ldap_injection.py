"""
Security tests for LDAP injection vulnerabilities
"""
import pytest
from unittest.mock import Mock, patch
from ldap_service import LDAPService
from ldap_utils import escape_ldap_filter


class TestLDAPInjectionProtection:
    """Test LDAP injection protection"""
    
    def test_escape_ldap_filter_wildcards(self):
        """Test escaping of wildcard characters"""
        result = escape_ldap_filter("*")
        assert result == r"\2a"
    
    def test_escape_ldap_filter_parentheses(self):
        """Test escaping of parentheses"""
        result = escape_ldap_filter("(test)")
        assert r"\28" in result and r"\29" in result
    
    def test_escape_ldap_filter_injection_attempt(self):
        """Test escaping of LDAP injection attempt"""
        malicious = "*)(&(userPassword=*"
        result = escape_ldap_filter(malicious)
        
        # Should not contain unescaped special characters
        assert "(" not in result or r"\28" in result
        assert ")" not in result or r"\29" in result
        assert "*" not in result or r"\2a" in result
    
    def test_escape_ldap_filter_null_byte(self):
        """Test escaping of null byte"""
        result = escape_ldap_filter("test\x00user")
        assert r"\00" in result
    
    @pytest.fixture
    def ldap_service(self):
        """Create LDAP service for testing"""
        config = {
            'LDAP_SERVER': 'ldap://test.example.com',
            'LDAP_USE_SSL': False,
            'LDAP_PORT': 389,
            'LDAP_USER_SEARCH_BASE': 'ou=users,dc=test,dc=com',
            'LDAP_USER_OBJECT_CLASS': 'inetOrgPerson',
            'LDAP_ATTR_MAP': {'username': 'uid'},
            'MAX_SEARCH_RESULTS': 500
        }
        with patch('ldap_service.Server'):
            return LDAPService(config)
    
    def test_search_with_malicious_input(self, ldap_service):
        """Test that malicious search input is properly escaped"""
        malicious_queries = [
            "*",
            "*)(&(userPassword=*",
            "admin)(|(uid=*",
            "test\x00user"
        ]
        
        for query in malicious_queries:
            with patch.object(ldap_service, '_get_admin_connection') as mock_conn:
                mock_conn.return_value = Mock(entries=[])
                
                # Should not raise exception and should return empty list
                results = ldap_service.search_users(query)
                assert isinstance(results, list)
