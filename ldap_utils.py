"""
Utilities for LDAP security - LDAP Injection Protection
"""
import re
from typing import Optional


def escape_ldap_filter(input_str: str) -> str:
    """
    Escape LDAP filter special characters to prevent LDAP injection
    
    Args:
        input_str: User input string
        
    Returns:
        Escaped string safe for LDAP filters
    """
    if not input_str:
        return input_str
    
    # Escape special LDAP filter characters
    replacements = {
        '\\': r'\5c',
        '*': r'\2a',
        '(': r'\28',
        ')': r'\29',
        '\x00': r'\00',  # NULL byte
    }
    
    for char, replacement in replacements.items():
        input_str = input_str.replace(char, replacement)
    
    return input_str


def escape_ldap_dn(input_str: str) -> str:
    """
    Escape DN special characters
    
    Args:
        input_str: User input string
        
    Returns:
        Escaped string safe for DN
    """
    if not input_str:
        return input_str
    
    # Escape DN special characters
    replacements = {
        '\\': r'\\',
        ',': r'\,',
        '+': r'\+',
        '"': r'\"',
        '<': r'\<',
        '>': r'\>',
        ';': r'\;',
        '=': r'\=',
        '\x00': r'\00',
    }
    
    for char, replacement in replacements.items():
        input_str = input_str.replace(char, replacement)
    
    return input_str


def validate_username(username: str) -> bool:
    """
    Validate username format
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not username or len(username) < 2 or len(username) > 64:
        return False
    
    # Allow alphanumeric, dots, hyphens, underscores
    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, username))


def validate_search_query(query: str) -> bool:
    """
    Validate search query
    
    Args:
        query: Search query to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not query:
        return True  # Empty query is valid
    
    if len(query) > 100:
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\x00',  # NULL bytes
        r'[()&|!].*[()&|!]',  # Multiple LDAP operators
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, query):
            return False
    
    return True


def validate_page_number(page: any) -> int:
    """
    Validate and sanitize page number
    
    Args:
        page: Page number (any type)
        
    Returns:
        Valid page number (minimum 1)
    """
    try:
        page_num = int(page)
        return max(1, min(page_num, 10000))  # Cap at 10000
    except (ValueError, TypeError):
        return 1
