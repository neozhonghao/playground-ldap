"""
LDAP Service Layer - Handles all LDAP operations with security fixes
"""
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES, Tls, ServerPool, ROUND_ROBIN
from ldap3.core.exceptions import LDAPException, LDAPBindError
import ssl
import logging
from typing import Optional, List, Dict, Any
from ldap_utils import escape_ldap_filter, escape_ldap_dn, validate_username, validate_search_query

logger = logging.getLogger(__name__)


class LDAPService:
    """Service class for LDAP operations with connection pooling and security fixes"""
    
    def __init__(self, config):
        self.config = config
        self.server = self._create_server()
        self._pool_connection = None
    
    def _create_server(self) -> Server:
        """Create LDAP server instance with SSL/TLS if configured"""
        try:
            if self.config['LDAP_USE_SSL']:
                # Configure TLS
                tls_config = Tls(
                    validate=ssl.CERT_REQUIRED,
                    version=ssl.PROTOCOL_TLSv1_2
                )
                server = Server(
                    self.config['LDAP_SERVER'],
                    port=self.config['LDAP_PORT'],
                    use_ssl=True,
                    tls=tls_config,
                    get_info=ALL
                )
            else:
                server = Server(
                    self.config['LDAP_SERVER'],
                    port=self.config['LDAP_PORT'],
                    get_info=ALL
                )
            
            logger.info(f"LDAP Server configured: {self.config['LDAP_SERVER']}:{self.config['LDAP_PORT']}")
            return server
            
        except Exception as e:
            logger.error(f"Error creating LDAP server: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user against LDAP with security fixes
        
        Args:
            username: User's login username
            password: User's password
            
        Returns:
            User data dict if authenticated, None otherwise
        """
        try:
            # Validate username format
            if not validate_username(username):
                logger.warning(f"Invalid username format attempted: {username[:20]}...")
                return None
            
            # Prevent empty password (anonymous bind vulnerability)
            if not password or len(password) == 0:
                logger.warning(f"Empty password attempt for user: {username}")
                return None
            
            # Escape username for DN to prevent LDAP injection
            escaped_username = escape_ldap_dn(username)
            
            # Construct user DN
            user_dn = f"{self.config['LDAP_USER_LOGIN_ATTR']}={escaped_username},{self.config['LDAP_USER_SEARCH_BASE']}"
            
            # Attempt to bind with user credentials
            conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            if conn.bound:
                # Fetch user attributes
                user_data = self.get_user_by_username(username)
                conn.unbind()
                
                logger.info(f"User authenticated successfully: {username}")
                return user_data
            
            return None
            
        except LDAPBindError as e:
            logger.warning(f"Authentication failed for user {username}")
            # Don't log detailed error to prevent information disclosure
            return None
        except Exception as e:
            logger.error(f"Error during authentication: {type(e).__name__}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user details by username with input validation"""
        try:
            # Validate username
            if not validate_username(username):
                logger.warning(f"Invalid username format in lookup: {username[:20]}...")
                return None
            
            conn = self._get_admin_connection()
            if not conn:
                return None
            
            # Escape username for filter
            escaped_username = escape_ldap_filter(username)
            
            search_filter = f"(&(objectClass={self.config['LDAP_USER_OBJECT_CLASS']})({self.config['LDAP_USER_LOGIN_ATTR']}={escaped_username}))"
            
            conn.search(
                search_base=self.config['LDAP_USER_SEARCH_BASE'],
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=ALL_ATTRIBUTES
            )
            
            if conn.entries:
                user_data = self._parse_ldap_entry(conn.entries[0])
                conn.unbind()
                return user_data
            
            conn.unbind()
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user {username}: {type(e).__name__}")
            return None
    
    def search_users(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for users in LDAP directory with LDAP injection protection
        
        Args:
            query: Search query string
            filters: Additional filters (department, title, etc.)
            
        Returns:
            List of user dictionaries
        """
        try:
            # Validate search query
            if query and not validate_search_query(query):
                logger.warning(f"Invalid search query detected: {query[:50]}...")
                return []
            
            conn = self._get_admin_connection()
            if not conn:
                return []
            
            # Build search filter with escaped input
            search_conditions = [
                f"(objectClass={self.config['LDAP_USER_OBJECT_CLASS']})"
            ]
            
            # Add query search across multiple fields with proper escaping
            if query:
                escaped_query = escape_ldap_filter(query)
                query_filter = f"(|(uid=*{escaped_query}*)(cn=*{escaped_query}*)(mail=*{escaped_query}*)(displayName=*{escaped_query}*))"
                search_conditions.append(query_filter)
            
            # Add additional filters with escaping
            if filters:
                for key, value in filters.items():
                    if value:
                        attr = self.config['LDAP_ATTR_MAP'].get(key, key)
                        escaped_value = escape_ldap_filter(str(value))
                        search_conditions.append(f"({attr}={escaped_value})")
            
            search_filter = f"(&{''.join(search_conditions)})"
            
            conn.search(
                search_base=self.config['LDAP_USER_SEARCH_BASE'],
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=ALL_ATTRIBUTES,
                size_limit=self.config['MAX_SEARCH_RESULTS']
            )
            
            results = [self._parse_ldap_entry(entry) for entry in conn.entries]
            conn.unbind()
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching users: {type(e).__name__}")
            return []
    
    def get_all_users(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        Get all users with pagination
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Dictionary with users list and pagination info
        """
        try:
            # Validate pagination parameters
            page = max(1, min(page, 10000))
            per_page = max(1, min(per_page, 500))
            
            conn = self._get_admin_connection()
            if not conn:
                return {'users': [], 'total': 0, 'page': page, 'per_page': per_page}
            
            search_filter = f"(objectClass={self.config['LDAP_USER_OBJECT_CLASS']})"
            
            conn.search(
                search_base=self.config['LDAP_USER_SEARCH_BASE'],
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=ALL_ATTRIBUTES
            )
            
            all_users = [self._parse_ldap_entry(entry) for entry in conn.entries]
            total = len(all_users)
            
            # Apply pagination
            start = (page - 1) * per_page
            end = start + per_page
            users = all_users[start:end]
            
            conn.unbind()
            
            return {
                'users': users,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"Error fetching all users: {type(e).__name__}")
            return {'users': [], 'total': 0, 'page': page, 'per_page': per_page}
    
    def get_departments(self) -> List[str]:
        """Get list of all departments"""
        try:
            conn = self._get_admin_connection()
            if not conn:
                return []
            
            search_filter = f"(objectClass={self.config['LDAP_USER_OBJECT_CLASS']})"
            
            conn.search(
                search_base=self.config['LDAP_USER_SEARCH_BASE'],
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['departmentNumber']
            )
            
            departments = set()
            for entry in conn.entries:
                if hasattr(entry, 'departmentNumber'):
                    dept = str(entry.departmentNumber.value) if entry.departmentNumber.value else None
                    if dept:
                        departments.add(dept)
            
            conn.unbind()
            return sorted(list(departments))
            
        except Exception as e:
            logger.error(f"Error fetching departments: {type(e).__name__}")
            return []
    
    def _get_admin_connection(self) -> Optional[Connection]:
        """Get connection with admin credentials for search operations"""
        try:
            conn = Connection(
                self.server,
                user=self.config['LDAP_BIND_DN'],
                password=self.config['LDAP_BIND_PASSWORD'],
                auto_bind=True
            )
            return conn
        except Exception as e:
            logger.error(f"Error creating admin connection: {type(e).__name__}")
            return None
    
    def _parse_ldap_entry(self, entry) -> Dict[str, Any]:
        """Parse LDAP entry into user dictionary"""
        user_data = {
            'dn': entry.entry_dn,
        }
        
        # Map LDAP attributes to user data
        for key, ldap_attr in self.config['LDAP_ATTR_MAP'].items():
            if hasattr(entry, ldap_attr):
                value = getattr(entry, ldap_attr).value
                user_data[key] = value if value else ''
        
        # Additional computed fields
        if 'first_name' in user_data and 'last_name' in user_data:
            user_data['full_name'] = f"{user_data['first_name']} {user_data['last_name']}".strip()
        elif 'display_name' in user_data:
            user_data['full_name'] = user_data['display_name']
        else:
            user_data['full_name'] = user_data.get('username', 'Unknown')
        
        return user_data
    
    def test_connection(self) -> bool:
        """Test LDAP connection"""
        try:
            conn = self._get_admin_connection()
            if conn:
                result = conn.bound
                conn.unbind()
                return result
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {type(e).__name__}")
            return False
