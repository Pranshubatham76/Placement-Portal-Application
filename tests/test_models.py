"""Tests for database models"""

import pytest
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from werkzeug.security import generate_password_hash


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, session):
        """Test creating a user"""
        user = User(
            email='test@example.com',
            password_hash=generate_password_hash('password'),
            role='student'
        )
        session.add(user)
        session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.role == 'student'
    
    def test_user_roles(self):
        """Test different user roles"""
        roles = ['admin', 'company', 'student']
        
        for role in roles:
            user = User(
                email=f'{role}@test.com',
                password_hash=generate_password_hash('password'),
                role=role
            )
            assert user.role == role


class TestStudentModel:
    """Test Student model"""
    
    def test_create_student(self, session, student_user):
        """Test creating a student profile"""
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        assert student is not None
        assert student.full_name == 'Test Student'
        assert student.branch == 'CSE'
        assert student.cgpa == 8.5


class TestCompanyModel:
    """Test Company model"""
    
    def test_create_company(self, session, company_user):
        """Test creating a company profile"""
        company = Company.query.filter_by(user_id=company_user.id).first()
        
        assert company is not None
        assert company.company_name == 'Test Company'
        assert company.approval_status == 'approved'


class TestPlacementDriveModel:
    """Test PlacementDrive model"""
    
    def test_create_drive(self, session, placement_drive):
        """Test creating a placement drive"""
        assert placement_drive.id is not None
        assert placement_drive.job_title == 'Software Engineer'
        assert placement_drive.status == 'approved'


class TestApplicationModel:
    """Test Application model"""
    
    def test_create_application(self, session, student_user, placement_drive):
        """Test creating an application"""
        from app.models.student import Student
        
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        application = Application(
            student_id=student.id,
            drive_id=placement_drive.id,
            status='applied'
        )
        session.add(application)
        session.commit()
        
        assert application.id is not None
        assert application.status == 'applied'
    
    def test_application_relationships(self, session, student_user, placement_drive):
        """Test application relationships"""
        from app.models.student import Student
        
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        application = Application(
            student_id=student.id,
            drive_id=placement_drive.id,
            status='applied'
        )
        session.add(application)
        session.commit()
        
        assert application.student is not None
        assert application.drive is not None
        assert application.student.full_name == 'Test Student'
        assert application.drive.job_title == 'Software Engineer'
