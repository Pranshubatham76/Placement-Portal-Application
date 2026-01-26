"""Tests for authentication service"""

import pytest
from app.services import auth_service


class TestAuthenticationService:
    """Test authentication service functions"""
    
    def test_register_student_success(self, session):
        """Test successful student registration"""
        success, data, message = auth_service.register_student(
            'newstudent@test.com',
            'password123'
        )
        
        assert success is True
        assert 'user' in data
        assert message == "Registration successful"
    
    def test_register_student_duplicate_email(self, session, student_user):
        """Test student registration with duplicate email"""
        success, data, message = auth_service.register_student(
            'student@test.com',
            'password123'
        )
        
        assert success is False
        assert message == "Email already registered"
    
    def test_authenticate_user_success(self, session, student_user):
        """Test successful authentication"""
        success, data, message = auth_service.authenticate_user(
            'student@test.com',
            'student123',
            remember=False
        )
        
        assert success is True
        assert 'next_route' in data
        assert message == "Login successful"
    
    def test_authenticate_user_invalid_credentials(self, session):
        """Test authentication with invalid credentials"""
        success, data, message = auth_service.authenticate_user(
            'invalid@test.com',
            'wrongpassword',
            remember=False
        )
        
        assert success is False
        assert message == "Invalid email or password"
    
    def test_register_company_success(self, session):
        """Test successful company registration"""
        company_data = {
            'company_name': 'New Company',
            'hr_name': 'HR Person',
            'hr_email': 'hr@newcompany.com',
            'hr_contact': '1234567890'
        }
        
        success, data, message = auth_service.register_company(
            'company@newcompany.com',
            'password123',
            company_data
        )
        
        assert success is True
        assert message == "Company registration successful. Pending admin approval."


class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_generate_otp(self, session, student_user):
        """Test OTP generation"""
        success, data, message = auth_service.generate_password_reset_otp(
            'student@test.com'
        )
        
        assert success is True
        assert 'otp' in data
        assert len(data['otp']) == 6
    
    def test_verify_otp_success(self, session, student_user):
        """Test OTP verification"""
        # Generate OTP first
        success, data, message = auth_service.generate_password_reset_otp(
            'student@test.com'
        )
        otp = data['otp']
        
        # Verify OTP
        success, data, message = auth_service.verify_otp(
            'student@test.com',
            otp
        )
        
        assert success is True
    
    def test_reset_password_success(self, session, student_user):
        """Test password reset"""
        # Generate and verify OTP
        success, data, message = auth_service.generate_password_reset_otp(
            'student@test.com'
        )
        otp = data['otp']
        
        auth_service.verify_otp('student@test.com', otp)
        
        # Reset password
        success, data, message = auth_service.reset_password(
            'student@test.com',
            'newpassword123'
        )
        
        assert success is True
        assert message == "Password reset successful"
