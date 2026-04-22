# Team Dashboard

A simple internal web application for team collaboration with LDAP/Active Directory authentication.

## Features

- **LDAP Authentication**: Login with corporate credentials
- **Team Directory**: Browse and search team members
- **Who's Online**: See who's currently active
- **Status Messages**: Share what you're working on
- **User Profiles**: View teammate information

## Quick Start

### 1. Install Dependencies

```bash
cd personal/projects/team-dashboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure LDAP

Copy `.env.example` to `.env` and configure your LDAP server:

```bash
cp .env.example .env
```

Edit `.env`:
```env
LDAP_SERVER=ldap://your-ldap-server.com
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=your-password
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
```

### 3. Run the Application

```bash
python app.py
```

Visit: `http://localhost:5001`

## Project Structure

```
team-dashboard/
├── app.py                  # Main Flask application
├── config.py               # Configuration
├── models.py               # Database models (SQLite)
├── ldap_auth.py            # LDAP authentication logic
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── index.html          # Dashboard home
│   ├── directory.html      # Team directory
│   └── profile.html        # User profile
└── team_dashboard.db       # SQLite database (created on first run)
```

## Usage

### Login
- Navigate to `http://localhost:5001`
- Enter your LDAP username and password
- Click "Sign In"

### Dashboard
- See who's online (active in last 30 minutes)
- Set your status message
- Quick links to directory and profile

### Team Directory
- Browse all team members
- Search by name, email, or department
- Click on a person to view their profile

### Profile
- View your own profile or teammates' profiles
- See status messages
- Update your own status

## Admin Features

### Sync Users from LDAP

Visit `/sync-ldap` to import all users from LDAP into the database. This is useful for pre-populating the directory.

## Security Notes

- Sessions expire after 30 minutes of inactivity
- LDAP credentials are never stored; authentication happens in real-time
- This is a simplified version for internal use
- For production, review and enhance security (add CSRF protection, rate limiting, etc.)

## Troubleshooting

**Can't connect to LDAP?**
- Check `LDAP_SERVER`, `LDAP_PORT` in `.env`
- Test with: `ldapsearch -x -H ldap://your-server -b "dc=example,dc=com"`

**ModuleNotFoundError?**
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**Database errors?**
- Delete `team_dashboard.db` and restart the app (creates fresh database)

## Development

To enable debug mode:
```bash
export FLASK_ENV=development
python app.py
```

## Future Enhancements

- [ ] Add role-based access control (RBAC)
- [ ] Org chart visualization
- [ ] Team chat/messaging
- [ ] Calendar integration
- [ ] Mobile app
- [ ] Profile photos

## License

Internal use only
