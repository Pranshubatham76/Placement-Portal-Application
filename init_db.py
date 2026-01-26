"""Database initialization and seed data script"""

from app import create_app, db, bcrypt
from app.models.user import User
from app.models.admin import Admin

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(role='admin').first()
        
        # Hash the password using bcrypt (Same as auth_service)
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')

        if existing_admin:
            print("⚠ Admin user already exists. Updating password to default 'admin123' to ensure valid salt...")
            existing_admin.password_hash = hashed_password
            db.session.commit()
            print("✓ Admin password updated successfully.")
        else:
            # Create default admin user
            print("Creating default admin user...")
            admin_user = User(
                email='admin@placement.com',
                password_hash=hashed_password,
                role='admin',
                is_active=True
            )
            
            db.session.add(admin_user)
            db.session.flush()  # Get the user ID
            
            # Create admin profile
            admin_profile = Admin(
                user_id=admin_user.id,
                name='System Administrator',
                designation='Placement Officer'
            )
            
            db.session.add(admin_profile)
            db.session.commit()
            
            print("✓ Default admin created successfully!")
            print("\nLogin Credentials:")
            print("Email: admin@placement.com")
            print("Password: admin123")
            print("\n⚠ IMPORTANT:Change the default password after first login!")


if __name__ == '__main__':
    init_database()
