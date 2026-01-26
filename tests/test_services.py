"""Tests for services layer"""

import pytest
from app.services import student_service, drive_service, application_service


class TestStudentService:
    """Test student service functions"""
    
    def test_create_student_profile(self, session, student_user):
        """Test creating student profile"""
        from app.models.student import Student
        
        # Delete existing student
        Student.query.filter_by(user_id=student_user.id).delete()
        session.commit()
        
        profile_data = {
            'full_name': 'New Student',
            'student_id': 'STU002',
            'contact': '9999999999',
            'branch': 'ECE',
            'cgpa': 9.0,
            'graduation_year': 2025
        }
        
        success, data, message = student_service.create_student_profile(
            student_user.id,
            profile_data
        )
        
        assert success is True
        assert 'student' in data
    
    def test_get_eligible_drives(self, session, student_user, placement_drive):
        """Test getting eligible drives for student"""
        from app.models.student import Student
        
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        success, data, message = student_service.get_eligible_drives(student.id)
        
        assert success is True
        assert 'drives' in data


class TestDriveService:
    """Test drive service functions"""
    
    def test_create_drive(self, session, company_user):
        """Test creating placement drive"""
        from app.models.company import Company
        
        company = Company.query.filter_by(user_id=company_user.id).first()
        
        drive_data = {
            'job_title': 'Data Analyst',
            'job_description': 'Data analysis role',
            'job_location': 'Mumbai',
            'job_type': 'full_time',
            'min_cgpa': 7.5,
            'eligible_branches': 'CSE,ECE,ME',
            'eligible_years': '2024',
            'ctc': 500000,
            'deadline': '2024-12-31'
        }
        
        success, data, message = drive_service.create_drive(
            company.id,
            drive_data
        )
        
        assert success is True
        assert 'drive' in data
    
    def test_get_company_drives(self, session, company_user, placement_drive):
        """Test getting company drives"""
        from app.models.company import Company
        
        company = Company.query.filter_by(user_id=company_user.id).first()
        
        success, data, message = drive_service.get_company_drives(company.id)
        
        assert success is True
        assert 'drives' in data
        assert len(data['drives']) > 0


class TestApplicationService:
    """Test application service functions"""
    
    def test_apply_to_drive(self, session, student_user, placement_drive):
        """Test student applying to drive"""
        from app.models.student import Student
        
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        success, data, message = application_service.apply_to_drive(
            student.id,
            placement_drive.id
        )
        
        assert success is True
        assert 'application' in data
    
    def test_duplicate_application(self, session, student_user, placement_drive):
        """Test duplicate application prevention"""
        from app.models.student import Student
        
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        # Apply first time
        application_service.apply_to_drive(student.id, placement_drive.id)
        
        # Try to apply again
        success, data, message = application_service.apply_to_drive(
            student.id,
            placement_drive.id
        )
        
        assert success is False
        assert "already applied" in message.lower()
    
    def test_update_application_status(self, session, student_user, placement_drive, company_user):
        """Test updating application status"""
        from app.models.student import Student
        
        student = Student.query.filter_by(user_id=student_user.id).first()
        
        # Create application
        success, data, message = application_service.apply_to_drive(
            student.id,
            placement_drive.id
        )
        application = data['application']
        
        # Update status
        success, data, message = application_service.update_application_status(
            application.id,
            'shortlisted',
            company_user.id,
            'Good performance'
        )
        
        assert success is True
        assert data['application'].status == 'shortlisted'
