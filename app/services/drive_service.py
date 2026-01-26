"""Placement Drive service - Drive CRUD and management"""

from datetime import datetime
from app import db
from app.models.placement_drive import PlacementDrive
from app.models.company import Company


def create_drive(company_id, drive_data):
    """
    Create new placement drive
    
    Args:
        company_id (int): Company ID
        drive_data (dict): Drive details
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Validate company
        company = Company.query.get(company_id)
        if not company:
            return (False, {}, "Company not found")
        
        if company.approval_status != 'approved':
            return (False, {}, "Company must be approved to create drives")
        
        # Parse dates
        application_deadline = None
        if drive_data.get('deadline'):
            try:
                application_deadline = datetime.strptime(drive_data.get('deadline'), '%Y-%m-%d')
            except ValueError:
                application_deadline = datetime.strptime(drive_data.get('deadline'), '%Y-%m-%dT%H:%M')

        # Create drive
        drive = PlacementDrive(
            company_id=company_id,
            job_title=drive_data.get('job_title'),
            job_description=drive_data.get('job_description'),
            job_location=drive_data.get('job_location'),
            job_type=drive_data.get('job_type'),
            min_cgpa=drive_data.get('min_cgpa'),
            eligible_branches=drive_data.get('eligible_branches'),  # comma-separated
            eligible_years=drive_data.get('eligible_years'),  # comma-separated
            ctc_min=drive_data.get('ctc_min') or drive_data.get('ctc'),
            ctc_max=drive_data.get('ctc_max'),
            application_deadline=application_deadline,
            drive_date=datetime.strptime(drive_data.get('drive_date'), '%Y-%m-%d') if drive_data.get('drive_date') else None,
            max_applicants=drive_data.get('max_applicants'),
            status='pending'  # Requires admin approval
        )
        
        db.session.add(drive)
        db.session.commit()
        
        return (True, {"drive": drive}, "Drive created successfully. Pending admin approval.")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Drive creation failed: {str(e)}")


def get_company_drives(company_id, status_filter=None):
    """
    Get all drives for a company
    
    Args:
        company_id (int): Company ID
        status_filter (str): Optional status filter
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = PlacementDrive.query.filter_by(company_id=company_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        drives = query.all()
        
        return (True, {"drives": drives}, f"Retrieved {len(drives)} drives")
    
    except Exception as e:
        return (False, {"drives": []}, f"Error: {str(e)}")


def get_drive_by_id(drive_id):
    """
    Get drive details
    
    Args:
        drive_id (int): Drive ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return (False, {}, "Drive not found")
        
        return (True, {"drive": drive}, "Drive retrieved successfully")
    
    except Exception as e:
        return (False, {}, f"Error: {str(e)}")


def update_drive(drive_id, drive_data, company_id=None):
    """
    Update placement drive
    
    Args:
        drive_id (int): Drive ID
        drive_data (dict): Updated drive data
        company_id (int): Company ID (for authorization)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return (False, {}, "Drive not found")
        
        # Verify ownership if company_id provided
        if company_id and drive.company_id != company_id:
            return (False, {}, "Unauthorized")
        
        # Cannot edit if closed
        if drive.status == 'closed':
            return (False, {}, "Cannot edit closed drive")
        
        # Update fields
        if 'job_title' in drive_data:
            drive.job_title = drive_data['job_title']
        if 'job_description' in drive_data:
            drive.job_description = drive_data['job_description']
        if 'job_location' in drive_data:
            drive.job_location = drive_data['job_location']
        if 'job_type' in drive_data:
            drive.job_type = drive_data['job_type']
        if 'min_cgpa' in drive_data:
            drive.min_cgpa = drive_data['min_cgpa']
        if 'eligible_branches' in drive_data:
            drive.eligible_branches = drive_data['eligible_branches']
        if 'eligible_years' in drive_data:
            drive.eligible_years = drive_data['eligible_years']
        if 'ctc_min' in drive_data:
            drive.ctc_min = drive_data['ctc_min']
        elif 'ctc' in drive_data:
            drive.ctc_min = drive_data['ctc']
        if 'ctc_max' in drive_data:
            drive.ctc_max = drive_data['ctc_max']
        if 'deadline' in drive_data:
            try:
                drive.application_deadline = datetime.strptime(drive_data['deadline'], '%Y-%m-%d')
            except ValueError:
                drive.application_deadline = datetime.strptime(drive_data['deadline'], '%Y-%m-%dT%H:%M')
        if 'drive_date' in drive_data:
            if drive_data['drive_date']:
                try:
                    drive.drive_date = datetime.strptime(drive_data['drive_date'], '%Y-%m-%d')
                except ValueError:
                    drive.drive_date = datetime.strptime(drive_data['drive_date'], '%Y-%m-%dT%H:%M')
            else:
                drive.drive_date = None
        if 'max_applicants' in drive_data:
            drive.max_applicants = drive_data['max_applicants']
        
        db.session.commit()
        
        return (True, {"drive": drive}, "Drive updated successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Update failed: {str(e)}")


def delete_drive(drive_id, company_id=None):
    """
    Delete placement drive
    
    Args:
        drive_id (int): Drive ID
        company_id (int): Company ID (for authorization)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return (False, {}, "Drive not found")
        
        # Verify ownership if company_id provided
        if company_id and drive.company_id != company_id:
            return (False, {}, "Unauthorized")
        
        # Check for applications
        from app.models.application import Application
        app_count = Application.query.filter_by(drive_id=drive_id).count()
        
        if app_count > 0:
            return (False, {}, f"Cannot delete drive with {app_count} applications")
        
        db.session.delete(drive)
        db.session.commit()
        
        return (True, {}, "Drive deleted successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Delete failed: {str(e)}")


def close_drive(drive_id, company_id=None):
    """
    Close placement drive
    
    Args:
        drive_id (int): Drive ID
        company_id (int): Company ID (for authorization)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return (False, {}, "Drive not found")
        
        # Verify ownership if company_id provided
        if company_id and drive.company_id != company_id:
            return (False, {}, "Unauthorized")
        
        if drive.status == 'closed':
            return (False, {}, "Drive already closed")
        
        drive.status = 'closed'
        db.session.commit()
        
        return (True, {"drive": drive}, "Drive closed successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Close failed: {str(e)}")


def get_all_drives(filters=None):
    """
    Get all drives (admin view)
    
    Args:
        filters (dict): Optional filters (status, company_id)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = PlacementDrive.query
        
        if filters:
            if 'status' in filters and filters['status']:
                query = query.filter_by(status=filters['status'])
            if 'company_id' in filters and filters['company_id']:
                query = query.filter_by(company_id=filters['company_id'])
        
        drives = query.all()
        
        return (True, {"drives": drives}, f"Retrieved {len(drives)} drives")
    
    except Exception as e:
        return (False, {"drives": []}, f"Error: {str(e)}")
