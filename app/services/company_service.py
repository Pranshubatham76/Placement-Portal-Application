"""Company service - Company profile and statistics"""

from app import db, mail
from app.models.company import Company
from app.models.user import User


def get_company_by_user_id(user_id):
    """
    Get company by user ID
    
    Args:
        user_id (int): User ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        company = Company.query.filter_by(user_id=user_id).first()
        
        if not company:
            return (False, {}, "Company profile not found")
        
        return (True, {"company": company}, "Company retrieved successfully")
    
    except Exception as e:
        return (False, {}, f"Error: {str(e)}")


def update_company_profile(company_id, profile_data, user_id=None):
    """
    Update company profile
    
    Args:
        company_id (int): Company ID
        profile_data (dict): Updated profile data
        user_id (int): User ID (for authorization)
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        company = Company.query.get(company_id)
        
        if not company:
            return (False, {}, "Company not found")
        
        # Verify ownership if user_id provided
        if user_id and company.user_id != user_id:
            return (False, {}, "Unauthorized")
        
        # Update fields
        if 'company_name' in profile_data:
            company.company_name = profile_data['company_name']
        if 'hr_name' in profile_data:
            company.hr_name = profile_data['hr_name']
        if 'hr_email' in profile_data:
            company.hr_email = profile_data['hr_email']
        if 'hr_contact' in profile_data:
            company.hr_contact = profile_data['hr_contact']
        if 'address' in profile_data:
            company.address = profile_data['address']
        if 'description' in profile_data:
            company.description = profile_data['description']
        if 'website' in profile_data:
            company.website = profile_data['website']
        
        db.session.commit()
        
        return (True, {"company": company}, "Profile updated successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Update failed: {str(e)}")
