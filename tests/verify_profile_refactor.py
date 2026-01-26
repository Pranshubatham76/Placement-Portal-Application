
import pytest
import sys
import os
sys.path.append(os.getcwd())

from io import BytesIO
from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.admin import Admin
from app.models.company import Company
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from app.services import student_service

def test_profile_refactor_integration():
    """
    Test the complete flow of student profile editing with single form
    and exception handling verification.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # 1. Setup Data
        user = User(
            email='test@student.com',
            password_hash='hash',
            role='student',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        # 2. Test Profile Creation (Success)
        profile_data = {
            'full_name': 'John Doe',
            'student_id': 'STU123',
            'contact': '1234567890',
            'branch': 'CSE',
            'cgpa': 9.0,
            'graduation_year': 2025,
            'linkedin_url': 'https://linkedin.com/in/johndoe',
            'github_url': 'https://github.com/johndoe'
        }
        
        success, data, msg = student_service.create_student_profile(user.id, profile_data)
        assert success is True
        student = data['student']
        assert student.linkedin_url == 'https://linkedin.com/in/johndoe'
        
        # 3. Test Profile Update (Success)
        update_data = {
            'full_name': 'John Updated',
            'linkedin_url': 'https://linkedin.com/in/johnupdated'
        }
        success, data, msg = student_service.update_student_profile(student.id, update_data)
        assert success is True
        assert data['student'].name == 'John Updated'
        
        # 4. Test Error Handling (Duplicate ID)
        # Create another user to try and claim same student_id
        user2 = User(email='test2@student.com', password_hash='hash', role='student', is_active=True)
        db.session.add(user2)
        db.session.commit()
        
        from app.utils.exceptions import StudentException
        
        # Try to create profile with same student_id (should fail if unique constraint exists, 
        # but let's force a failure or check what triggers it. 
        # Actually student_id is unique in model.
        
        profile_data_dup = profile_data.copy()
        try:
            student_service.create_student_profile(user2.id, profile_data_dup)
            assert False, "Should have raised StudentException"
        except StudentException as e:
            # Check if message is the generic one
            assert "Failed to create profile" in str(e)
        except Exception as e:
            print(f"CAUGHT UNEXPECTED EXCEPTION: {type(e).__name__}: {e}")
            # If it's IntegrityError, it means service layer didn't wrap it.
            # But service layer HAS try-except Exception.
            # Reraise to see traceback if needed or fail assertion
            assert False, f"Expected StudentException, got {type(e).__name__}"
            
        print("Verification passed!")

if __name__ == "__main__":
    test_profile_refactor_integration()
