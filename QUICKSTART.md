# LDAP Employee Directory - Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] LDAP server accessible (OpenLDAP or Active Directory)
- [ ] Redis installed and running
- [ ] LDAP credentials available

## 5-Minute Setup

### Step 1: Installation (2 minutes)

```bash
cd projects/ldap
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configuration (2 minutes)

```bash
cp .env.example .env
```

Edit `.env`:
```env
LDAP_SERVER=ldap://your-server.com
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=your-password
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### Step 3: Start Redis

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

### Step 4: Run Application (1 minute)

```bash
python app.py
```

Visit: http://localhost:5000

## Troubleshooting

**Can't connect to LDAP?**
```bash
# Test connection
ldapsearch -x -H ldap://your-server -D "cn=admin,dc=example,dc=com" -W
```

**Redis not running?**
```bash
redis-cli ping  # Should return PONG
```

**Import errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

## Quick Test

1. Navigate to http://localhost:5000
2. Login with your LDAP credentials
3. Browse the employee directory
4. Search for a colleague
5. View a user profile

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Set `LDAP_USE_SSL=True`
3. Use strong `SECRET_KEY`
4. Configure Redis for sessions
5. Deploy behind Nginx/Apache
6. Enable HTTPS

See [README.md](README.md) for detailed instructions.

## Getting Help

- Check application logs
- Review README.md troubleshooting section
- Verify LDAP connectivity separately
- Ensure Redis is running

## Security Notes

⚠️ **Important Security Features Enabled:**
- ✅ LDAP injection protection
- ✅ CSRF protection
- ✅ Rate limiting
- ✅ Input validation
- ✅ Session security
- ✅ Audit logging

All security features are enabled by default!

## Next Steps

1. Customize LDAP attribute mapping in `config.py`
2. Adjust rate limits for your environment
3. Configure audit logging destination
4. Set up monitoring and alerts
5. Run the test suite: `pytest`

---

**Need more help?** See the comprehensive [README.md](README.md)
