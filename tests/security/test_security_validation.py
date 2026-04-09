"""
Security tests for input validation
"""
import pytest
from ldap_utils import validate_username, validate_search_query, validate_page_number


class TestInputValidation:
    """Test input validation functions"""
    
    def test_validate_username_valid(self):
        """Test valid usernames"""
        valid_usernames = [
            'user',
            'test.user',
            'john-doe',
            'user_123',
            'a1b2c3',
        ]
        
        for username in valid_usernames:
            assert validate_username(username) is True
    
    def test_validate_username_invalid(self):
        """Test invalid usernames"""
        invalid_usernames = [
            '',  # Empty
            'a',  # Too short
            'a' * 100,  # Too long
            'user@domain',  # Invalid character
            '../admin',  # Path traversal
            'user\nname',  # Newline
            'user<script>',  # XSS attempt
        ]
        
        for username in invalid_usernames:
            assert validate_username(username) is False
    
    def test_validate_search_query_valid(self):
        """Test valid search queries"""
        valid_queries = [
            '',  # Empty is valid
            'john',
            'john doe',
            'engineer',
        ]
        
        for query in valid_queries:
            assert validate_search_query(query) is True
    
    def test_validate_search_query_invalid(self):
        """Test invalid search queries"""
        invalid_queries = [
            'a' * 200,  # Too long
            '\x00test',  # Null byte
            '()&|test',  # LDAP operators
        ]
        
        for query in invalid_queries:
            assert validate_search_query(query) is False
    
    def test_validate_page_number(self):
        """Test page number validation"""
        assert validate_page_number(1) == 1
        assert validate_page_number(100) == 100
        assert validate_page_number(0) == 1  # Minimum is 1
        assert validate_page_number(-5) == 1  # Negative becomes 1
        assert validate_page_number(999999) == 10000  # Capped at 10000
        assert validate_page_number('invalid') == 1  # Invalid returns 1
        assert validate_page_number(None) == 1  # None returns 1
