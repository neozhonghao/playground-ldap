# LDAP Employee Directory & Authentication System

A secure, production-ready web application for enterprise employee directory management with LDAP authentication. Built with Flask and featuring comprehensive security measures including LDAP injection protection, CSRF protection, and rate limiting.

## 🌟 Features

- **Secure LDAP Authentication** - Single Sign-On with LDAP/Active Directory
- **Employee Directory** - Browse and search employees with pagination
- **Advanced Search** - Search by name, email, username, or department
- **User Profiles** - View detailed employee information
- **Security Hardened** - LDAP injection protection, CSRF protection, rate limiting
- **Responsive Design** - Modern Bootstrap-based UI
- **Audit Logging** - Track user activities for compliance
- **Production Ready** - Connection pooling, error handling, health checks

## 🔒 Security Features

✅ **LDAP Injection Protection** - All user inputs are properly escaped  
✅ **CSRF Protection** - Flask-WTF CSRF tokens on all forms  
✅ **Rate Limiting** - Prevent brute force attacks  
✅ **Input Validation** - Comprehensive validation on all inputs  
✅ **Session Security** - Secure cookie settings, Redis-backed sessions  
✅ **Empty Password Prevention** - Blocks anonymous LDAP bind attempts  
✅ **Audit Logging** - Security event logging  
✅ **Error Handling** - No information disclosure in errors  

## 📋 Requirements

- Python 3.8+
- LDAP Server (OpenLDAP or Active Directory)
- Redis (for sessions and rate limiting)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd projects/ldap

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your LDAP server settings:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# LDAP Server Configuration
LDAP_SERVER=ldap://your-ldap-server.com
LDAP_PORT=389
LDAP_USE_SSL=False

# LDAP Bind Credentials
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=your-bind-password

# LDAP Search Configuration
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
LDAP_USER_OBJECT_CLASS=inetOrgPerson
LDAP_USER_LOGIN_ATTR=uid

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 3. Start Redis

```bash
# macOS with Homebrew
brew services start redis

# Linux
sudo systemctl start redis

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

### 4. Run the Application

```bash
# Development
python app.py

# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Visit http://localhost:5000

## 📁 Project Structure

```
ldap/
├── app.py                  # Main Flask application
├── config.py               # Configuration management
├── ldap_service.py         # LDAP integration layer
├── ldap_utils.py           # Security utilities (injection protection)
├── auth.py                 # Authentication module
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # Frontend JavaScript
│
├── templates/
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   ├── directory.html      # Employee directory
│   ├── profile.html        # User profile
│   ├── search.html         # Search page
│   ├── 404.html            # Error pages
│   ├── 403.html
│   ├── 429.html
│   └── 500.html
│
└── tests/
    ├── unit/
    │   ├── test_ldap_service.py
    │   ├── test_auth.py
    │   └── test_app.py
    ├── security/
    │   ├── test_security_ldap_injection.py
    │   ├── test_security_auth.py
    │   └── test_security_validation.py
    └── integration/
        └── test_integration_flows.py
```

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-flask

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/security/
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_ldap_service.py -v
```

## 🔧 Configuration Details

### LDAP Attribute Mapping

The application maps LDAP attributes to user fields. Customize in `config.py`:

```python
LDAP_ATTR_MAP = {
    'username': 'uid',
    'email': 'mail',
    'first_name': 'givenName',
    'last_name': 'sn',
    'display_name': 'displayName',
    'department': 'departmentNumber',
    'title': 'title',
    'phone': 'telephoneNumber',
    'mobile': 'mobile',
    'employee_id': 'employeeNumber',
    'manager': 'manager',
}
```

### Rate Limiting

Rate limits are configured per endpoint:

- **Login**: 5 requests per minute
- **Search**: 30 requests per minute
- **API Endpoints**: 30 requests per minute
- **Global**: 200 requests per day, 50 per hour

### Session Configuration

Sessions are stored in Redis with:
- **Session Lifetime**: 1 hour (3600 seconds)
- **Secure Cookies**: Enabled in production
- **HTTPOnly**: Enabled
- **SameSite**: Lax

## 🛡️ Security Best Practices

### For Development

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use strong SECRET_KEY** - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
3. **Keep dependencies updated** - Regularly run `pip list --outdated`

### For Production

1. **Enable SSL/TLS** - Set `LDAP_USE_SSL=True`
2. **Use Redis for sessions** - Not filesystem-based
3. **Enable secure cookies** - Set `SESSION_COOKIE_SECURE=True`
4. **Set strong SECRET_KEY** - Use environment variable
5. **Configure firewall** - Limit access to LDAP and Redis ports
6. **Enable audit logging** - Set `ENABLE_AUDIT_LOG=True`
7. **Use HTTPS** - Deploy behind reverse proxy (Nginx/Apache)
8. **Monitor logs** - Set up log aggregation and monitoring

## 📊 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Login handler
- `GET /logout` - Logout handler

### Application Routes
- `GET /` - Home (redirects to dashboard)
- `GET /dashboard` - Main dashboard
- `GET /directory` - Employee directory with pagination
- `GET /search` - Search page
- `GET /profile/<username>` - View user profile
- `GET /profile` - View own profile

### API Routes
- `GET /api/departments` - Get all departments
- `GET /api/search?q=<query>` - Autocomplete search
- `GET /api/health` - Health check endpoint

## 🐛 Troubleshooting

### LDAP Connection Failed

```bash
# Test LDAP connection
ldapsearch -x -H ldap://your-server -D "cn=admin,dc=example,dc=com" -W

# Check logs
tail -f /var/log/syslog  # Linux
log show --predicate 'process == "python"' --last 1h  # macOS
```

### Redis Connection Failed

```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission Denied

```bash
# Check file permissions
ls -la

# Fix permissions
chmod +x app.py
```

## 🔄 Deployment

### Using Gunicorn (Production)

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# With logging
gunicorn -w 4 -b 0.0.0.0:8000 app:app --access-logfile - --error-logfile -
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Using Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📈 Performance Optimization

1. **Enable Connection Pooling** - Already implemented in ldap_service.py
2. **Use Redis Caching** - Cache frequently accessed data
3. **Enable Compression** - Use gzip in production
4. **CDN for Static Files** - Serve CSS/JS from CDN
5. **Database Layer** - Consider syncing LDAP to database for read-heavy workloads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Test LDAP connectivity separately
- Verify Redis is running

## ⚠️ Important Notes

1. **LDAP Credentials** - Store securely, never commit to version control
2. **SSL/TLS** - Always use in production for LDAP connections
3. **Rate Limiting** - Adjust limits based on your user base
4. **Session Security** - Use Redis in production, not filesystem
5. **Input Validation** - All user inputs are validated and escaped
6. **Audit Logging** - Enable for compliance and security monitoring

## 🎯 Production Checklist

- [ ] Set strong `SECRET_KEY` in environment
- [ ] Enable `LDAP_USE_SSL=True`
- [ ] Configure Redis for sessions
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Enable audit logging
- [ ] Configure rate limits appropriately
- [ ] Set up HTTPS with SSL certificate
- [ ] Configure firewall rules
- [ ] Set up log monitoring
- [ ] Configure automated backups
- [ ] Test disaster recovery procedures
- [ ] Document operational procedures

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [ldap3 Documentation](https://ldap3.readthedocs.io/)
- [LDAP Best Practices](https://ldap.com/ldap-best-practices/)
- [OWASP Security Guidelines](https://owasp.org/)

---

Built with ❤️ using Flask and LDAP
