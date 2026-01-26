"""Student service - Student profile and eligibility management"""

from app import db
from app.models.student import Student
from app.models.user import User
import logging
from app.utils.exceptions import StudentException
from app.utils.validators import validate_phone_number
logger = logging.getLogger(__name__)

def get_student_by_user_id(user_id):
    """
    Get student by user ID
    
    Args:
        user_id (int): User ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            raise StudentException("Can not proceed without completing your profile")
        logger.info(f"Student retrieved successfully: {student}")
        return (True, {"student": student}, "Student retrieved successfully")
    
    except Exception as e:
        logger.error(f"Error fetching student profile: {str(e)}")
        raise StudentException("Unable to retrieve student profile. Please try again.")


def create_student_profile(user_id, profile_data):
    """
    Create student profile
    
    Args:
        user_id (int): User ID
        profile_data (dict): Profile data
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Check if profile already exists
        existing = Student.query.filter_by(user_id=user_id).first()
        if existing:
            raise StudentException("Profile already exists")

        validate_phone_number(profile_data['contact'])

        # Create student profile
        student = Student(
            user_id=user_id,
            name=profile_data.get('full_name'),
            student_id=profile_data.get('student_id'),
            contact=profile_data.get('contact'),
            branch=profile_data.get('branch'),
            cgpa=profile_data.get('cgpa'),
            graduation_year=profile_data.get('graduation_year'),
            skills=profile_data.get('skills', ''),
            address=profile_data.get('address', ''),
            linkedin_url=profile_data.get('linkedin_url', ''),
            github_url=profile_data.get('github_url', ''),
            resume_path=profile_data.get('resume_path', '')
        )
        
        db.session.add(student)
        db.session.commit()
        logger.info(f"Profile created successfully: {student}")
        return (True, {"student": student}, "Profile created successfully")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating profile: {str(e)}")
        raise StudentException("Failed to create profile. Please check your data and try again.")


def update_student_profile(student_id, profile_data):
    """
    Update student profile
    
    Args:
        student_id (int): Student ID
        profile_data (dict): Updated profile data
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        student = Student.query.get(student_id)
        
        if not student:
            raise StudentException("Student not found")
        
        # Update fields
        if 'full_name' in profile_data:
            student.name = profile_data['full_name']
        if 'student_id' in profile_data:
            student.student_id = profile_data['student_id']
        if 'contact' in profile_data:
            student.contact = profile_data['contact']
        if 'branch' in profile_data:
            student.branch = profile_data['branch']
        if 'cgpa' in profile_data:
            student.cgpa = profile_data['cgpa']
        if 'graduation_year' in profile_data:
            student.graduation_year = profile_data['graduation_year']
        if 'skills' in profile_data:
            student.skills = profile_data['skills']
        if 'address' in profile_data:
            student.address = profile_data['address']
        
        db.session.commit()
        logger.info(f"Profile updated successfully: {student}")
        return (True, {"student": student}, "Profile updated successfully")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        raise StudentException("Failed to update profile. Please try again.")


def get_eligible_drives(student_id):
    """
    Get drives eligible for a student
    
    Args:
        student_id (int): Student ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        from app.models.placement_drive import PlacementDrive
        from app.utils.validators import check_eligibility
        from datetime import datetime
        
        student = Student.query.get(student_id)
        if not student:
            raise StudentException("Student not found")
        
        # Get all approved drives
        all_drives = PlacementDrive.query.filter_by(status='approved').all()
        
        eligible_drives = []
        for drive in all_drives:
            # Check if deadline hasn't passed
            if drive.deadline >= datetime.utcnow():
                is_eligible, reasons = check_eligibility(student, drive)
                if is_eligible:
                    eligible_drives.append(drive)
        logger.info(f"Eligible drives: {eligible_drives}")
        return (True, {"drives": eligible_drives, "count": len(eligible_drives)},
                f"Found {len(eligible_drives)} eligible drives")
    
    except Exception as e:
        logger.error(f"Error fetching drives: {str(e)}")
        raise StudentException("Unable to load placement drives. Please try again.")
