from datetime import datetime
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    alternative_id = db.Column(db.String(20), nullable=True) # Used to store the alternative id of the user
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for query optimization
    __table_args__ = (
        db.Index('idx_users_active_blacklist', 'is_active', 'is_blacklisted'),
        db.Index('idx_users_email', 'email'),
        db.Index('idx_users_role', 'role'),
        
    )
    
    def __repr__(self):
        return f'<User {self.email}>'
