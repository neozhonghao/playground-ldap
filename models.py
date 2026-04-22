"""
Database models for Team Dashboard
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(200))
    full_name = db.Column(db.String(200))
    department = db.Column(db.String(100))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    status = db.relationship('StatusMessage', backref='user', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_online(self):
        """Check if user is online (active in last 30 minutes)"""
        from datetime import timedelta
        if not self.last_seen:
            return False
        threshold = datetime.utcnow() - timedelta(minutes=30)
        return self.last_seen >= threshold

class StatusMessage(db.Model):
    """User status message model"""
    __tablename__ = 'status_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    message = db.Column(db.String(200), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StatusMessage user_id={self.user_id}>'

def init_db():
    """Initialize database tables"""
    db.create_all()
