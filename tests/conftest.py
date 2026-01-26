"""Test configuration and fixtures for pytest"""

import pytest
from app import create_app, db
from app.models.user import User
from app.models.admin import Admin
from app.models.company import Company
from app.models.student import Student
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    return app


@pytest.fixture(scope='session')
def _db(app):
    """Create database for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture(scope='function')
def session(_db):
    """Create a new database session for a test"""
    connection = _db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)
    
    _db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def admin_user(session):
    """Create admin user"""
    user = User(
        email='admin@test.com',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    session.add(user)
    session.commit()
    
    admin = Admin(
        user_id=user.id,
        name='Test Admin',
        designation='Placement Officer'
    )
    session.add(admin)
    session.commit()
    
    return user


@pytest.fixture
def company_user(session):
    """Create company user"""
    user = User(
        email='company@test.com',
        password_hash=generate_password_hash('company123'),
        role='company',
        is_active=True
    )
    session.add(user)
    session.commit()
    
    company = Company(
        user_id=user.id,
        company_name='Test Company',
        hr_name='HR Manager',
        hr_email='hr@test.com',
        hr_contact='1234567890',
        approval_status='approved'
    )
    session.add(company)
    session.commit()
    
    return user


@pytest.fixture
def student_user(session):
    """Create student user"""
    user = User(
        email='student@test.com',
        password_hash=generate_password_hash('student123'),
        role='student',
        is_active=True
    )
    session.add(user)
    session.commit()
    
    student = Student(
        user_id=user.id,
        name='Test Student',
        student_id='STU001',
        contact='9876543210',
        branch='CSE',
        cgpa=8.5,
        graduation_year=2024
    )
    session.add(student)
    session.commit()
    
    return user


@pytest.fixture
def placement_drive(session, company_user):
    """Create placement drive"""
    from app.models.company import Company
    
    company = Company.query.filter_by(user_id=company_user.id).first()
    
    drive = PlacementDrive(
        company_id=company.id,
        job_title='Software Engineer',
        job_description='Test job description',
        job_location='Test City',
        job_type='full_time',
        min_cgpa=7.0,
        eligible_branches='CSE,ECE',
        eligible_years='2024,2025',
        ctc=600000,
        deadline='2024-12-31',
        status='approved'
    )
    session.add(drive)
    session.commit()
    
    return drive
