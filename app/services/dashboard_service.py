"""Dashboard service - Statistics and analytics for all roles"""

from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from flask_login import current_user


def get_admin_dashboard_stats():
    """
    Get admin dashboard statistics
    
    Returns:
        dict: Dashboard statistics
    """
    try:
        stats = {
            'total_students': Student.query.count(),
            'total_companies': Company.query.count(),
            'total_drives': PlacementDrive.query.count(),
            'active_drives': PlacementDrive.query.filter_by(status='approved').count(),
            'total_applications': Application.query.count(),
            'pending_companies': Company.query.filter_by(approval_status='pending').count(),
            'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
            'placements_success_rate': _calculate_success_rate()
        }
        return stats
    except Exception as e:
        return {}


def get_company_dashboard_stats(company_id):
    """
    Get company dashboard statistics
    
    Args:
        company_id (int): Company ID
    
    Returns:
        dict: Dashboard statistics
    """
    try:
        drives = PlacementDrive.query.filter_by(company_id=company_id).all()
        drive_ids = [d.id for d in drives]
        
        stats = {
            'total_drives': len(drives),
            'approved_drives': PlacementDrive.query.filter_by(company_id=company_id, status='approved').count(),
            'pending_drives': PlacementDrive.query.filter_by(company_id=company_id, status='pending').count(),
            'total_applicants': Application.query.filter(Application.drive_id.in_(drive_ids)).count() if drive_ids else 0,
            'shortlisted': Application.query.filter(Application.drive_id.in_(drive_ids), Application.status=='shortlisted').count() if drive_ids else 0,
            'selected': Application.query.filter(Application.drive_id.in_(drive_ids), Application.status=='selected').count() if drive_ids else 0
        }
        return stats
    except Exception as e:
        return {}


def get_student_dashboard_stats(student_id):
    """
    Get student dashboard statistics
    
    Args:
        student_id (int): Student ID
    
    Returns:
        dict: Dashboard statistics
    """
    try:
        student = Student.query.get(student_id)
        
        stats = {
            'profile_complete': _check_profile_completion(student),
            'total_applications': Application.query.filter_by(student_id=student_id).count(),
            'shortlisted': Application.query.filter_by(student_id=student_id, status='shortlisted').count(),
            'selected': Application.query.filter_by(student_id=student_id, status='selected').count(),
            'rejected': Application.query.filter_by(student_id=student_id, status='rejected').count(),
            'available_drives': PlacementDrive.query.filter_by(status='approved').count()
        }
        return stats
    except Exception as e:
        return {}


def _calculate_success_rate():
    """Calculate placement success rate"""
    total_apps = Application.query.count()
    if total_apps == 0:
        return 0.0
    
    selected = Application.query.filter_by(status='selected').count()
    return round((selected / total_apps) * 100, 2)


def _check_profile_completion(student):
    """Check if student profile is complete"""
    if not student:
        return False
    
    required_fields = [
        student.full_name,
        student.student_id,
        student.contact,
        student.branch,
        student.cgpa,
        student.graduation_year,
        student.resume_path
    ]
    
    return all(field is not None and field != '' for field in required_fields)
