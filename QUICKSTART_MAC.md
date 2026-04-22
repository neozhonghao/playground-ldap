# Quick Start: OpenLDAP on macOS (Apple Silicon)

Simplified setup for your specific system.

---

## Paths for Your System

- **Config directory:** `/opt/homebrew/etc/openldap/`
- **Binary:** `/opt/homebrew/opt/openldap/libexec/slapd`
- **Schema directory:** `/opt/homebrew/etc/openldap/schema/`
- **Data directory:** `/opt/homebrew/var/openldap-data/` (we'll create this)

---

## Setup Steps

### 1. Install OpenLDAP

```bash
brew install openldap
```

### 2. Create data directory

```bash
sudo mkdir -p /opt/homebrew/var/openldap-data
sudo chmod 700 /opt/homebrew/var/openldap-data
sudo chown $(whoami) /opt/homebrew/var/openldap-data
```

### 3. Generate admin password hash

```bash
slappasswd -s admin123
```

**Copy the output!** (looks like `{SSHA}abc123...`)
{SSHA}txewTW+HkQJB+CM5qUe+Kk8fziikr4Gb

### 4. Edit slapd.conf

Edit `/opt/homebrew/etc/openldap/slapd.conf`:

```bash
nano /opt/homebrew/etc/openldap/slapd.conf
```

Replace the entire file with this:

```conf
# Schema
include /opt/homebrew/etc/openldap/schema/core.schema
include /opt/homebrew/etc/openldap/schema/cosine.schema
include /opt/homebrew/etc/openldap/schema/inetorgperson.schema
include /opt/homebrew/etc/openldap/schema/nis.schema

# PID and args files
pidfile /opt/homebrew/var/run/slapd.pid
argsfile /opt/homebrew/var/run/slapd.args

# Database
database mdb
suffix "dc=example,dc=com"
rootdn "cn=admin,dc=example,dc=com"
rootpw PASTE_YOUR_HASHED_PASSWORD_HERE
directory /opt/homebrew/var/openldap-data
index objectClass eq

# Access control
access to attrs=userPassword
    by self write
    by anonymous auth
    by * none

access to *
    by self write
    by * read
```

**Replace `PASTE_YOUR_HASHED_PASSWORD_HERE` with your hash from step 2.**

Save and exit (Ctrl+O, Enter, Ctrl+X).

### 5. Start LDAP server

```bash
sudo /opt/homebrew/opt/openldap/libexec/slapd \
  -f /opt/homebrew/etc/openldap/slapd.conf \
  -h "ldap://127.0.0.1:389"
```

To run in background, add `&` at the end.

### 6. Test connection

```bash
ldapsearch -x -H ldap://localhost -b "dc=example,dc=com" \
  -D "cn=admin,dc=example,dc=com" -w admin123
```

Should return without errors (empty result is fine for now).

### 7. Add base structure

```bash
cd ~/Desktop/neozhonghao/personal/projects/team-dashboard
ldapadd -x -D "cn=admin,dc=example,dc=com" -w admin123 -f ldif/base.ldif
```

### 8. Add test users

```bash
ldapadd -x -D "cn=admin,dc=example,dc=com" -w admin123 -f ldif/users.ldif
```

### 9. Verify users exist

```bash
ldapsearch -x -H ldap://localhost -b "ou=users,dc=example,dc=com" \
  -D "cn=admin,dc=example,dc=com" -w admin123
```

You should see your 5 test users!

### 10. Update Team Dashboard config

Copy and edit `.env`:

```bash
cd ~/Desktop/neozhonghao/personal/projects/team-dashboard
cp .env.example .env
nano .env
```

Set these values:

```env
LDAP_SERVER=ldap://localhost
LDAP_PORT=389
LDAP_USE_SSL=False
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=admin123
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
LDAP_USER_OBJECT_CLASS=inetOrgPerson
LDAP_USER_LOGIN_ATTR=uid
```

### 11. Test Team Dashboard

```bash
cd ~/Desktop/neozhonghao/personal/projects/team-dashboard
source venv/bin/activate
python app.py
```

Go to http://localhost:5001 and login:
- Username: `jdoe`
- Password: `password123`

---

## Quick Commands

**Start LDAP:**
```bash
sudo /opt/homebrew/opt/openldap/libexec/slapd -f /opt/homebrew/etc/openldap/slapd.conf -h "ldap://127.0.0.1:389" &
```

**Stop LDAP:**
```bash
sudo killall slapd
```

**Check if running:**
```bash
ps aux | grep slapd
```

**Search all users:**
```bash
ldapsearch -x -H ldap://localhost -b "ou=users,dc=example,dc=com" -D "cn=admin,dc=example,dc=com" -w admin123
```

---

## Troubleshooting

**"Address already in use" error?**
```bash
sudo lsof -i :389
sudo killall slapd
```

**Can't write to data directory?**
```bash
sudo chown -R $(whoami) /opt/homebrew/var/openldap-data
```

**slapd won't start?**

Run in debug mode to see errors:
```bash
sudo /opt/homebrew/opt/openldap/libexec/slapd -d 1 -f /opt/homebrew/etc/openldap/slapd.conf
```

---

## Uninstall

```bash
# Stop LDAP
sudo killall slapd

# Uninstall
brew uninstall openldap

# Remove data
sudo rm -rf /opt/homebrew/var/openldap-data
```
