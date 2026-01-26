"""Application service - Application submission and management"""

from datetime import datetime
from app import db
from app.models.application import Application
from app.models.student import Student
from app.models.placement_drive import PlacementDrive
from app.utils.validators import check_eligibility


def apply_to_drive(student_id, drive_id):
    """
    Submit student application to placement drive
    
    Args:
        student_id (int): Student IDdrive_id (int): Drive ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Get student and drive
        student = Student.query.get(student_id)
        drive = PlacementDrive.query.get(drive_id)
        
        if not student:
            return (False, {}, "Student not found")
        
        if not drive:
            return (False, {}, "Placement drive not found")
        
        # Check if drive is approved and active
        if drive.status != 'approved':
            return (False, {}, "This drive is not accepting applications")
        
        # Check deadline
        if drive.deadline < datetime.utcnow():
            return (False, {}, "Application deadline has passed")
        
        # Check for duplicate application
        existing_app = Application.query.filter_by(
            student_id=student_id,
            drive_id=drive_id
        ).first()
        
        if existing_app:
            return (False, {}, "You have already applied to this drive")
        
        # Check eligibility
        is_eligible, reasons = check_eligibility(student, drive)
        
        if not is_eligible:
            reason_text = "; ".join(reasons)
            return (False, {}, f"Not eligible: {reason_text}")
        
        # Create application
        application = Application(
            student_id=student_id,
            drive_id=drive_id,
            status='applied',
            applied_at=datetime.utcnow()
        )
        
        db.session.add(application)
        db.session.commit()
        
        return (True, {"application": application}, "Application submitted successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Application failed: {str(e)}")


def get_student_applications(student_id, status_filter=None):
    """
    Get all applications for a student
    
    Args:
        student_id (int): Student ID
        status_filter (str): Optional status filter
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = Application.query.filter_by(student_id=student_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        applications = query.all()
        
        return (True, {"applications": applications}, 
                f"Retrieved {len(applications)} applications")
    
    except Exception as e:
        return (False, {"applications": []}, f"Error: {str(e)}")


def get_drive_applications(drive_id, status_filter=None):
    """
    Get all applications for a drive
    
    Args:
        drive_id (int): Drive ID
        status_filter (str): Optional status filter
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = Application.query.filter_by(drive_id=drive_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        applications = query.all()
        
        return (True, {"applications": applications}, 
                f"Retrieved {len(applications)} applications")
    
    except Exception as e:
        return (False, {"applications": []}, f"Error: {str(e)}")


def update_application_status(application_id, new_status, updated_by=None, notes=None):
    """
    Update application status (company action)
    
    Args:
        application_id (int): Application ID
        new_status (str): New status (shortlisted/selected/rejected)
        updated_by (int): User ID who updated
        notes (str): Optional notes
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        application = Application.query.get(application_id)
        
        if not application:
            return (False, {}, "Application not found")
        
        # Valid status transitions
        valid_statuses = ['applied', 'shortlisted', 'selected', 'rejected']
        if new_status not in valid_statuses:
            return (False, {}, "Invalid status")
        
        # Update application
        application.status = new_status
        application.status_updated_at = datetime.utcnow()
        
        if updated_by:
            application.updated_by = updated_by
        
        if notes:
            application.company_notes = notes
        
        db.session.commit()
        
        return (True, {"application": application}, f"Status updated to {new_status}")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Update failed: {str(e)}")


def withdraw_application(application_id, student_id):
    """
    Withdraw application (student action)
    
    Args:
        application_id (int): Application ID
        student_id (int): Student ID (for verification)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        application = Application.query.get(application_id)
        
        if not application:
            return (False, {}, "Application not found")
        
        # Verify ownership
        if application.student_id != student_id:
            return (False, {}, "Unauthorized")
        
        # Can only withdraw if status is 'applied'
        if application.status != 'applied':
            return (False, {}, "Cannot withdraw application in current status")
        
        # Delete application
        db.session.delete(application)
        db.session.commit()
        
        return (True, {}, "Application withdrawn successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Withdrawal failed: {str(e)}")
