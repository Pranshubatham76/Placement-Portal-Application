"""Integration tests for routes"""

import pytest
from flask import url_for


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, student_user):
        """Test successful login"""
        response = client.post('/auth/login', data={
            'email': 'student@test.com',
            'password': 'student123',
            'remember': False
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_logout(self, client, student_user):
        """Test logout"""
        # Login first
        client.post('/auth/login', data={
            'email': 'student@test.com',
            'password': 'student123'
        })
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


class TestStudentRoutes:
    """Test student routes"""
    
    def test_student_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/student/dashboard')
        assert response.status_code in [302, 401]
    
    def test_student_dashboard_authenticated(self, client, student_user):
        """Test authenticated student can access dashboard"""
        # Login
        client.post('/auth/login', data={
            'email': 'student@test.com',
            'password': 'student123'
        })
        
        # Access dashboard
        response = client.get('/student/dashboard')
        assert response.status_code == 200


class TestCompanyRoutes:
    """Test company routes"""
    
    def test_company_dashboard_requires_login(self, client):
        """Test company dashboard requires authentication"""
        response = client.get('/company/dashboard')
        assert response.status_code in [302, 401]
    
    def test_company_dashboard_authenticated(self, client, company_user):
        """Test authenticated company can access dashboard"""
        # Login
        client.post('/auth/login', data={
            'email': 'company@test.com',
            'password': 'company123'
        })
        
        # Access dashboard
        response = client.get('/company/dashboard')
        assert response.status_code == 200


class TestAdminRoutes:
    """Test admin routes"""
    
    def test_admin_dashboard_requires_admin(self, client, student_user):
        """Test admin dashboard requires admin role"""
        # Login as student
        client.post('/auth/login', data={
            'email': 'student@test.com',
            'password': 'student123'
        })
        
        # Try to access admin dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code in [302, 403]
    
    def test_admin_dashboard_authenticated(self, client, admin_user):
        """Test authenticated admin can access dashboard"""
        # Login as admin
        client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        # Access dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
