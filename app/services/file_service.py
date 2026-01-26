"""File service - Resume upload/download/delete functionality"""

import os
from werkzeug.utils import secure_filename
from app import db
from app.models.student import Student
from app.utils.validators import validate_resume_file
from app.utils.helpers import generate_unique_filename, sanitize_filename
from app.utils.constants import ALLOWED_RESUME_EXTENSIONS, MAX_RESUME_SIZE_BYTES
from flask import current_app


def upload_resume(student_id, file):
    """
    Upload student resume
    
    Args:
        student_id (int): Student ID
        file: FileStorage object
    
    Returns:
        tuple: (success, data, message)
    """
    # Validate file
    is_valid, message = validate_resume_file(file)
    if not is_valid:
        return (False, {}, message)
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return (False, {}, "Student not found")
        
        # Delete old resume if exists
        if student.resume_path:
            _delete_file(student.resume_path)
        
        # Save new file
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename, prefix=f"student_{student_id}")
        
        # Get upload folder path
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'resumes')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Update student record
        student.resume_path = f"uploads/resumes/{unique_filename}"
        db.session.commit()
        
        return (True, {"resume_path": student.resume_path}, "Resume uploaded successfully")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Upload failed: {str(e)}")


def delete_resume(student_id):
    """
    Delete student resume
    
    Args:
        student_id (int): Student ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return (False, {}, "Student not found")
        
        if not student.resume_path:
            return (False, {}, "No resume to delete")
        
        # Delete file
        success = _delete_file(student.resume_path)
        
        if success:
            # Update student record
            student.resume_path = None
            db.session.commit()
            return (True, {}, "Resume deleted successfully")
        else:
            return (False, {}, "Failed to delete resume file")
    
    except Exception as e:
        db.session.rollback()
        return (False, {}, f"Delete failed: {str(e)}")


def get_resume_path(student_id):
    """
    Get student resume file path
    
    Args:
        student_id (int): Student ID
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return (False, {}, "Student not found")
        
        if not student.resume_path:
            return (False, {}, "No resume uploaded")
        
        # Check if file exists
        file_path = os.path.join(current_app.root_path, 'static', student.resume_path)
        if not os.path.exists(file_path):
            return (False, {}, "Resume file not found")
        
        return (True, {"resume_path": student.resume_path, "full_path": file_path}, 
                "Resume found")
    
    except Exception as e:
        return (False, {}, f"Error: {str(e)}")


def _delete_file(relative_path):
    """
    Delete file from filesystem
    
    Args:
        relative_path (str): Relative path from static folder
    
    Returns:
        bool: Success status
    """
    try:
        file_path = os.path.join(current_app.root_path, 'static', relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"File deletion error: {str(e)}")
        return False
