"""Admin service layer - Business logic for admin operations"""

from app.models.user import User
from app.models.student import Student
from app.models.company import Company  
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from app import db


def get_dashboard_stats():
    """
    Get admin dashboard statistics
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Total students count
        students = Student.query.count()
        
        # Total companies count
        companies = Company.query.count()
        
        # Total placement drives count
        placements = PlacementDrive.query.count()
        
        # Total application count
        applications = Application.query.count()
        
        # Pending company approvals count
        companies_approval = Company.query.filter_by(approval_status="pending").count()
        
        # Pending drive approvals count
        drive_approval = PlacementDrive.query.filter_by(status="pending").count()
        
        # Placement success rate
        total_apps = Application.query.count()
        if total_apps > 0:
            success_rate = (Application.query.filter_by(status="selected").count() / total_apps) * 100
        else:
            success_rate = 0.0
        
        data = {
            "total_students": students,
            "total_companies": companies,
            "total_placements": placements,
            "total_applications": applications,
            "pending_company_approval": companies_approval,
            "pending_drive_approval": drive_approval,
            "placement_success_rate": round(success_rate, 2)
        }
        
        return (True, data, "Dashboard statistics retrieved successfully")
        
    except Exception as e:
        return (False, {}, f"Error fetching dashboard stats: {str(e)}")


def get_all_companies(filters=None):
    """
    Get all companies with optional filters
    
    Args:
        filters (dict): Filter criteria (approval_status, etc.)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = Company.query
        
        if filters:
            if 'approval_status' in filters and filters['approval_status']:
                query = query.filter_by(approval_status=filters['approval_status'])
        
        companies = query.all()
        
        return (True, {"companies": companies}, f"Retrieved {len(companies)} companies")
        
    except Exception as e:
        return (False, {"companies": []}, f"Error fetching companies: {str(e)}")


def get_company_by_id(company_id):
    """
    Get company by ID
    
    Args:
        company_id (int): Company ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        company = Company.query.get(company_id)
        
        if not company:
            return (False, {}, "Company not found")
        
        return (True, {"company": company}, "Company retrieved successfully")
        
    except Exception as e:
        return (False, {}, f"Error fetching company: {str(e)}")


def update_company(company_id, company_data):
    """
    Update company information
    
    Args:
        company_id (int): Company ID
        company_data (dict): Updated company data
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        company = Company.query.get(company_id)
        
        if not company:
            return (False, {}, "Company not found")
        
        # Validate required fields
        required_fields = ['company_name', 'hr_name', 'hr_email', 'hr_contact']
        for field in required_fields:
            if field in company_data and not company_data[field]:
                return (False, {}, f"{field.replace('_', ' ').title()} is required")
        
        # Update company fields
        if 'company_name' in company_data:
            company.company_name = company_data['company_name']
        if 'hr_name' in company_data:
            company.hr_name = company_data['hr_name']
        if 'hr_email' in company_data:
            company.hr_email = company_data['hr_email']
        if 'hr_contact' in company_data:
            company.hr_contact = company_data['hr_contact']
        if 'address' in company_data:
            company.address = company_data['address']
        if 'description' in company_data:
            company.description = company_data['description']
        if 'website' in company_data:
            company.website = company_data['website']
        
        db.session.commit()
        
        return (True, {"company": company}, "Company updated successfully")
        
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Error updating company: {str(e)}")


def delete_company(company_id):
    """
    Delete company after validation
    
    Args:
        company_id (int): Company ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Check existence
        company = Company.query.get(company_id)
        if not company:
            return (False, {}, "Company does not exist")
        
        # Check for placement drives
        drive = PlacementDrive.query.filter_by(company_id=company_id).first()
        if drive:
            return (False, {}, "Cannot delete company with existing placement drives")
        
        # Delete company
        db.session.delete(company)
        db.session.commit()
        
        return (True, {}, "Company deleted successfully")
        
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Error deleting company: {str(e)}")


def approve_company(company_id):
    """
    Approve a company registration
    
    Args:
        company_id (int): Company ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        company = Company.query.get(company_id)
        
        if not company:
            return (False, {}, "Company not found")
        
        if company.approval_status == "approved":
            return (False, {}, "Company already approved")
        
        company.approval_status = "approved"
        db.session.commit()
        
        return (True, {"company": company}, "Company approved successfully")
        
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Error approving company: {str(e)}")


def reject_company(company_id, reason=None):
    """
    Reject a company registration
    
    Args:
        company_id (int): Company ID
        reason (str): Rejection reason
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        company = Company.query.get(company_id)
        
        if not company:
            return (False, {}, "Company not found")
        
        company.approval_status = "rejected"
        if reason:
            company.rejection_reason = reason
        
        db.session.commit()
        
        return (True, {"company": company}, "Company rejected successfully")
        
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Error rejecting company: {str(e)}")


def get_all_students(filters=None):
    """
    Get all students with optional filters
    
    Args:
        filters (dict): Filter criteria (branch, year, cgpa, etc.)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = Student.query
        
        if filters:
            if 'branch' in filters and filters['branch']:
                query = query.filter_by(branch=filters['branch'])
            if 'graduation_year' in filters and filters['graduation_year']:
                query = query.filter_by(graduation_year=filters['graduation_year'])
        
        students = query.all()
        
        return (True, {"students": students}, f"Retrieved {len(students)} students")
        
    except Exception as e:
        return (False, {"students": []}, f"Error fetching students: {str(e)}")


def get_student_by_id(student_id):
    """
    Get student by ID
    
    Args:
        student_id (int): Student ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        student = Student.query.get(student_id)
        
        if not student:
            return (False, {}, "Student not found")
        
        return (True, {"student": student}, "Student retrieved successfully")
        
    except Exception as e:
        return (False, {}, f"Error fetching student: {str(e)}")


def approve_drive(drive_id):
    """
    Approve a placement drive
    
    Args:
        drive_id (int): Drive ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return (False, {}, "Placement drive not found")
        
        if drive.status == "approved":
            return (False, {}, "Drive already approved")
        
        drive.status = "approved"
        db.session.commit()
        
        return (True, {"drive": drive}, "Placement drive approved successfully")
        
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Error approving drive: {str(e)}")


def reject_drive(drive_id, reason=None):
    """
    Reject a placement drive
    
    Args:
        drive_id (int): Drive ID
        reason (str): Rejection reason
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return (False, {}, "Placement drive not found")
        
        drive.status = "rejected"
        if reason:
            drive.rejection_reason = reason
        
        db.session.commit()
        
        return (True, {"drive": drive}, "Placement drive rejected successfully")
        
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Error rejecting drive: {str(e)}")