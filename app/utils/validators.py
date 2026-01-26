"""Custom validators for forms and business logic"""

import os
import re
from app.utils.exceptions import AuthException
from app.utils.constants import (
    ALLOWED_RESUME_EXTENSIONS,
    MAX_RESUME_SIZE_BYTES,
    BRANCHES,
    JOB_TYPES
)
from app.models.admin import Admin
from app.models.company import Company
from app.models.student import Student

def validate_file_extension(filename, allowed_extensions=None):
    """
    Validate file extension
    
    Args:
        filename (str): Filename to validate
        allowed_extensions (set): Set of allowed extensions
    
    Returns:
        tuple: (is_valid, message)
    """
    if not filename:
        return (False, "No file provided")
    
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_RESUME_EXTENSIONS
    
    if '.' not in filename:
        return (False, "File has no extension")
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in allowed_extensions:
        return (False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}")
    
    return (True, "File extension valid")


def validate_file_size(file, max_size_bytes=None):
    """
    Validate file size
    
    Args:
        file: FileStorage object
        max_size_bytes (int): Maximum file size in bytes
    
    Returns:
        tuple: (is_valid, message)
    """
    if max_size_bytes is None:
        max_size_bytes = MAX_RESUME_SIZE_BYTES
    
    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > max_size_bytes:
        max_size_mb = max_size_bytes / (1024 * 1024)
        return (False, f"File too large. Maximum size: {max_size_mb}MB")
    
    if file_size == 0:
        return (False, "File is empty")
    
    return (True, "File size valid")


def validate_resume_file(file):
    """
    Comprehensive resume file validation
    
    Args:
        file: FileStorage object
    
    Returns:
        tuple: (is_valid, message)
    """
    if not file or file.filename == '':
        return (False, "No file selected")
    
    # Validate extension
    is_valid, message = validate_file_extension(file.filename, ALLOWED_RESUME_EXTENSIONS)
    if not is_valid:
        return (False, message)
    
    # Validate size
    is_valid, message = validate_file_size(file, MAX_RESUME_SIZE_BYTES)
    if not is_valid:
        return (False, message)
    
    return (True, "Resume file valid")


def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email to validate
    
    Returns:
        tuple: (is_valid, message)
    """
    if not email:
        return (False, "Email is required")
    
    # Basic email regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        return (False, "Invalid email format")
    
    return (True, "Email valid")


def validate_phone(phone):
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        tuple: (is_valid, message)
    """
    if not phone:
        return (False, "Phone number is required")
    
    # Remove spaces and dashes
    phone_clean = phone.replace(' ', '').replace('-', '')
    
    # Check if all digits
    if not phone_clean.isdigit():
        return (False, "Phone number must contain only digits")
    
    # Check length (10 digits for India)
    if len(phone_clean) != 10:
        return (False, "Phone number must be 10 digits")
    
    return (True, "Phone number valid")


def validate_cgpa(cgpa):
    """
    Validate CGPA value
    
    Args:
        cgpa (float): CGPA to validate
    
    Returns:
        tuple: (is_valid, message)
    """
    if cgpa is None:
        return (False, "CGPA is required")
    
    try:
        cgpa_float = float(cgpa)
    except (ValueError, TypeError):
        return (False, "CGPA must be a number")
    
    if cgpa_float < 0.0 or cgpa_float > 10.0:
        return (False, "CGPA must be between 0.0 and 10.0")
    
    return (True, "CGPA valid")


def validate_branch(branch):
    """
    Validate academic branch
    
    Args:
        branch (str): Branch to validate
    
    Returns:
        tuple: (is_valid, message)
    """
    if not branch:
        return (False, "Branch is required")
    
    if branch not in BRANCHES:
        return (False, f"Invalid branch. Valid branches: {', '.join(BRANCHES)}")
    
    return (True, "Branch valid")


def check_eligibility(student, drive):
    """
    Check if student is eligible for a placement drive
    
    Args:
        student (Student): Student object
        drive (PlacementDrive): PlacementDrive object
    
    Returns:
        tuple: (is_eligible, reasons)
            is_eligible (bool): Whether student is eligible
            reasons (list): List of ineligibility reasons
    """
    ineligibility_reasons = []
    
    # Check resume uploaded
    if not student.resume_path:
        ineligibility_reasons.append("Resume not uploaded")
    
    # Check CGPA requirement
    if student.cgpa < drive.min_cgpa:
        ineligibility_reasons.append(f"CGPA {student.cgpa} is below minimum {drive.min_cgpa}")
    
    # Check branch eligibility
    if drive.eligible_branches:
        eligible_branches_list = [b.strip() for b in drive.eligible_branches.split(',')]
        if student.branch not in eligible_branches_list:
            ineligibility_reasons.append(f"Branch {student.branch} not eligible")
    
    # Check graduation year
    if drive.eligible_years:
        eligible_years_list = [int(y.strip()) for y in drive.eligible_years.split(',')]
        if student.graduation_year not in eligible_years_list:
            ineligibility_reasons.append(f"Graduation year {student.graduation_year} not eligible")
    
    # Check if drive is still open
    from datetime import datetime
    if drive.deadline < datetime.utcnow():
        ineligibility_reasons.append("Application deadline has passed")
    
    is_eligible = len(ineligibility_reasons) == 0
    
    return (is_eligible, ineligibility_reasons)


def validate_password_strength(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (is_valid, message)
    """
    if not password:
        raise AuthException("Password is required")
    
    if len(password) < 8:
        raise AuthException("Password must be at least 8 characters long")
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise AuthException("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise AuthException("Password must contain at least one lowercase letter")
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise AuthException("Password must contain at least one digit")
    
    return True

def validate_phone_number(phone_number):
    """
    Validate phone number format
    
    Args:
        phone_number (str): Phone number to validate
    
    Returns:
        tuple: (is_valid, message)
    """
    if not phone_number:
        raise AuthException("Phone number is required")
    
    # Remove spaces and dashes
    phone_clean = phone_number.replace(' ', '').replace('-', '')
    
    # Check if all digits
    if not phone_clean.isdigit():
        raise AuthException("Phone number must contain only digits")
    
    # Check length (10 digits for India)
    if len(phone_clean) != 10:
        raise AuthException("Phone number must be 10 digits")

    # Check nor student nor company nor admin have same number
    if Admin.query.filter_by(contact=phone_clean).first() or Student.query.filter_by(contact=phone_clean).first() or Company.query.filter_by(contact=phone_clean).first():
        raise AuthException("Phone number already exists")
    
    return True

