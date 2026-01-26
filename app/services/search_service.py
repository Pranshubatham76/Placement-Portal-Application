"""Search service - Advanced search functionality"""

from app.models.student import Student
from app.models.company import Company
from sqlalchemy import or_


def search_students(filters=None):
    """
    Search students with various criteria
    
    Args:
        filters (dict): Search criteria
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = Student.query
        
        if filters:
            # Name search (partial match)
            if 'name' in filters and filters['name']:
                query = query.filter(Student.full_name.ilike(f"%{filters['name']}%"))
            
            # Student ID search (exact match)
            if 'student_id' in filters and filters['student_id']:
                query = query.filter_by(student_id=filters['student_id'])
            
            # Contact search (exact match)
            if 'contact' in filters and filters['contact']:
                query = query.filter_by(contact=filters['contact'])
            
            # Email search (exact match)
            if 'email' in filters and filters['email']:
                # Need to join with User table
                from app.models.user import User
                query = query.join(User).filter(User.email == filters['email'])
            
            # Branch filter
            if 'branch' in filters and filters['branch']:
                query = query.filter_by(branch=filters['branch'])
            
            # Graduation year filter
            if 'graduation_year' in filters and filters['graduation_year']:
                query = query.filter_by(graduation_year=filters['graduation_year'])
        
        students = query.all()
        
        return (True, {'students': students, 'count': len(students)}, 
                f"Found {len(students)} students")
    
    except Exception as e:
        return (False, {'students': [], 'count': 0}, f"Search failed: {str(e)}")


def search_companies(filters=None):
    """
    Search companies with various criteria
    
    Args:
        filters (dict): Search criteria
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        query = Company.query
        
        if filters:
            # Company name search (partial match)
            if 'company_name' in filters and filters['company_name']:
                query = query.filter(Company.company_name.ilike(f"%{filters['company_name']}%"))
            
            # HR name search (partial match)
            if 'hr_name' in filters and filters['hr_name']:
                query = query.filter(Company.hr_name.ilike(f"%{filters['hr_name']}%"))
        
        companies = query.all()
        
        return (True, {'companies': companies, 'count': len(companies)}, 
                f"Found {len(companies)} companies")
    
    except Exception as e:
        return (False, {'companies': [], 'count': 0}, f"Search failed: {str(e)}")
