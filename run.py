from app import create_app, db
# Import ALL models so db.create_all() can create all tables
from app.models.user import User
from app.models.admin import Admin
from app.models.company import Company
from app.models.student import Student
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from app.utils.loggings import logging
from init_db import init_database

app = create_app()

if __name__ == "__main__":
    # # Initialize the database
    # with app.app_context():
    #     db.create_all()
    #     print("✓ Database tables created successfully!")
    init_database()
    
    app.run(debug=True)