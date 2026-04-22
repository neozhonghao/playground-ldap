"""
LDAP authentication module
Simplified version - adapt from playground-ldap for production use
"""
import ldap
from flask import current_app

def authenticate_ldap(username, password):
    """
    Authenticate user against LDAP server
    
    Args:
        username: User's username (uid)
        password: User's password
        
    Returns:
        dict: User information if authenticated, None otherwise
    """
    if not username or not password:
        return None
    
    try:
        # Construct user DN
        user_dn = f"{current_app.config['LDAP_USER_LOGIN_ATTR']}={username},{current_app.config['LDAP_USER_SEARCH_BASE']}"
        
        # Connect to LDAP
        ldap_uri = f"{current_app.config['LDAP_SERVER']}:{current_app.config['LDAP_PORT']}"
        conn = ldap.initialize(ldap_uri)
        
        if current_app.config['LDAP_USE_SSL']:
            conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            conn.start_tls_s()
        
        # Set timeout
        conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5.0)
        
        # Try to bind with user credentials
        conn.simple_bind_s(user_dn, password)
        
        # If bind successful, search for user attributes
        search_filter = f"({current_app.config['LDAP_USER_LOGIN_ATTR']}={username})"
        attributes = ['cn', 'mail', 'ou', 'displayName']
        
        result = conn.search_s(
            current_app.config['LDAP_USER_SEARCH_BASE'],
            ldap.SCOPE_SUBTREE,
            search_filter,
            attributes
        )
        
        conn.unbind_s()
        
        if result:
            dn, attrs = result[0]
            return {
                'username': username,
                'name': attrs.get('cn', [username.encode()])[0].decode('utf-8'),
                'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                'department': attrs.get('ou', [b''])[0].decode('utf-8') if attrs.get('ou') else ''
            }
        
        return None
        
    except ldap.INVALID_CREDENTIALS:
        return None
    except ldap.SERVER_DOWN:
        current_app.logger.error('LDAP server is down')
        return None
    except Exception as e:
        current_app.logger.error(f'LDAP authentication error: {str(e)}')
        return None

def get_all_users_from_ldap():
    """
    Retrieve all users from LDAP (for sync)
    
    Returns:
        list: List of user dicts
    """
    try:
        ldap_uri = f"{current_app.config['LDAP_SERVER']}:{current_app.config['LDAP_PORT']}"
        conn = ldap.initialize(ldap_uri)
        
        if current_app.config['LDAP_USE_SSL']:
            conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            conn.start_tls_s()
        
        # Bind with admin credentials
        conn.simple_bind_s(
            current_app.config['LDAP_BIND_DN'],
            current_app.config['LDAP_BIND_PASSWORD']
        )
        
        # Search for all users
        search_filter = f"(objectClass={current_app.config['LDAP_USER_OBJECT_CLASS']})"
        attributes = ['uid', 'cn', 'mail', 'ou']
        
        results = conn.search_s(
            current_app.config['LDAP_USER_SEARCH_BASE'],
            ldap.SCOPE_SUBTREE,
            search_filter,
            attributes
        )
        
        conn.unbind_s()
        
        users = []
        for dn, attrs in results:
            if attrs.get('uid'):
                users.append({
                    'username': attrs['uid'][0].decode('utf-8'),
                    'name': attrs.get('cn', [b''])[0].decode('utf-8'),
                    'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                    'department': attrs.get('ou', [b''])[0].decode('utf-8') if attrs.get('ou') else ''
                })
        
        return users
        
    except Exception as e:
        current_app.logger.error(f'LDAP sync error: {str(e)}')
        return []
