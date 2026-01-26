"""Authentication service layer - Business logic for user authentication"""

from app.models.user import User
from app.models.company import Company
from app.models.student import Student
from app import bcrypt, db, mail
from flask_login import login_user, logout_user
import random
# from flask_mail import Message
from app.celery_app.tasks import send_email
from config import Config
from app.utils.validators import validate_password_strength, validate_email, validate_phone_number
from app.utils.exceptions import AuthException
import logging

# Set logging
logger = logging.getLogger(__name__)

def register_user(email, password):
    """
    Register a new student user
    
    Args:
        email (str): User email
        password (str): User password
        role (str): User role
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Check if data is available
        validate_password_strength(password)
        validate_email(email)
        # Check if user already exists
        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
          raise AuthException("User already exists")
    
    
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        
        # Generate random alphanumeric id
        alternative_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
        
        # Create new user
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role="student",
            alternative_id=alternative_id,
            is_active=True,
            is_blacklisted=False,
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcoming mail asynchronously
        try:
            from app.celery_app.helpers import send_welcome_email
            send_welcome_email(email, user_type="student")
        except Exception as mail_error:
            # Log mail error but don't fail registration
            logger.error(f"Mail sending failed: {str(mail_error)}")

        
        logger.info("User registered successfully!")
        return (True, {"user": new_user}, "User registered successfully! Please log in.")
        
    except AuthException as e:
        logger.error(f"Registration failed: {str(e)}")
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {str(e)}")
        raise AuthException("Registration failed")


def register_company(email, password, company_data):
    """
    Register a new company (requires admin approval)
    
    Args:
        email (str): Company email
        password (str): Password
        company_data (dict): Company details
    
    Returns:
        tuple: (success, data, message)
    """
    # # Validate required fields
    # if not email or not password:
    #     return (False, {}, "Email and password are required")
    
    required_company_fields = ['company_name', 'hr_name', 'hr_email', 'hr_contact', 'website', 'address', 'description']
    for field in required_company_fields:
        if field not in company_data or not company_data[field]:
            return (False, {}, f"{field.replace('_', ' ').title()} is required")

    try:
        validate_email(email)
        validate_password_strength(password)
        validate_phone_number(company_data['hr_contact'])
        validate_email(company_data['hr_email'])
        
        # Check if user already exists
        # user_exist = User.query.filter_by(email=email).first()
        # if user_exist:
        #   return (False, {}, "User already exists")
    
    
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        
        # Generate alternative ID
        alternative_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
        
        # Create new user
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role="company",
            alternative_id=alternative_id,
            is_active=True,
            is_blacklisted=False,
        )
        db.session.add(new_user)
        db.session.flush()  # Get user ID
        
        # Create company profile
        new_company = Company(
            user_id=new_user.id,
            company_name=company_data['company_name'],
            hr_name=company_data['hr_name'],
            hr_email=company_data['hr_email'],
            hr_contact=company_data['hr_contact'],
            address=company_data.get('address', ''),
            description=company_data.get('description', ''),
            website=company_data.get('website', ''),
            approval_status='pending'
        )
        db.session.add(new_company)
        db.session.commit()


        #  Send email to company asynchronously
        try:
            from app.celery_app.helpers import send_welcome_email
            send_welcome_email(email, user_type="company")
        except Exception as mail_error:
            # Log mail error but don't fail registration
            logger.error(f"Mail sending failed: {str(mail_error)}")
        
        logger.info("Company registered successfully! Pending admin approval")
        return (True, {"user": new_user, "company": new_company}, 
                "Company registered successfully! Pending admin approval.")
    
    except AuthException as e:
        logger.error(f"Company registration failed: {str(e)}")
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Company registration failed: {str(e)}")
        raise AuthException("Registration failed")


def authenticate_user(email, password, remember=False):
    try:
        if not email or not password:
            raise AuthException("Email and password are required") # 400

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            logger.warning(f"Failed login attempt for email: {email}")
            raise AuthException("Invalid email or password")# 401

        if user.is_blacklisted:
            logger.warning(f"Blacklisted user login attempt: {email}")
            raise AuthException("Your account has been blacklisted. Please contact support.")#403

        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {email}")
            raise AuthException("Your account is not active. Please contact support.")#403

        if user.role == "company":
            company = Company.query.filter_by(user_id=user.id).first()
            if company and company.approval_status != "approved":
                logger.warning(f"Pending company login attempt: {email}")
                raise AuthException("Your company registration is pending admin approval.")

        login_user(user, remember=remember, fresh=True)
        
        logger.info(f"User logged in successfully: {email}")

        role_routes = {
            "admin": "admin.dashboard",
            "company": "company.dashboard",
            "student": "student.dashboard",
        }

        return {
            "user": user,
            "next_route": role_routes.get(user.role, "index"),
            "message": f"Welcome back, {user.email}!",
        }

    except AuthException:
        raise

    except Exception as e:
        logger.error(f"Login error for {email}: {str(e)}")
        raise AuthException("An unexpected error occurred. Please try again later.")


def logout_user_service():
    """
    Logout user and destroy session
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        logout_user()
        logger.info("User logged out successfully")
        return (True, {}, "You have been logged out successfully.")
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise AuthException(f"Logout failed: {str(e)}")


def generate_password_reset_otp(email):
    """
    Generate OTP for password reset
    
    Args:
        email (str): User email
    
    Returns:
        tuple: (success, data, message) - data contains 'otp' and 'email'
    """
    try:
        # check data validity
        validate_email(email)

        # check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            raise AuthException("User not found")
        
        # Generate OTP
        otp = ''.join(random.choices('0123456789', k=6))
        
        # Send OTP to user asynchronously
        try:
            from app.celery_app.helpers import send_otp_email
            send_otp_email(email, otp)
        except Exception as mail_error:
            logger.error(f"OTP mail sending failed: {str(mail_error)}")
            raise AuthException("Failed to send OTP email. Please try again later.")
        
        logger.info(f"Password reset OTP sent to {email}")
        return (True, {"otp": otp, "email": email}, "OTP sent to your email")
    
    except AuthException:
        raise
    except Exception as e:
        logger.error(f"OTP generation failed for {email}: {str(e)}")
        raise AuthException(f"Failed to send OTP: {str(e)}")


def reset_password_with_otp(email, otp, session_otp, new_password):
    """
    Reset password using OTP
    
    Args:
        email (str): User email
        otp (str): OTP entered by user
        session_otp (str): OTP stored in session
        new_password (str): New password
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        # Check if data is available
        if not otp:
            raise AuthException("OTP is required")

        validate_password_strength(new_password)
        validate_email(email)
        
        if not session_otp:
            raise AuthException("Invalid session. Please request a new OTP.")
    
        # Check if OTP matches
        if otp != session_otp:
            raise AuthException("Invalid OTP")
        
        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        
        # Update user password
        user = User.query.filter_by(email=email).first()
        if not user:
            raise AuthException("User not found")
        
        user.password_hash = hashed_password
        db.session.commit()
        
        logger.info(f"Password reset successful for {email}")
        return (True, {}, "Password reset successfully")
        
    except AuthException:
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset failed for {email}: {str(e)}")
        raise AuthException(f"Password reset failed: {str(e)}")


def verify_password(user, password):
    """
    Verify user password for re-authentication
    
    Args:
        user (User): User object
        password (str): Password to verify
    
    Returns:
        tuple: (success, data, message)
    """
    try:
        validate_password_strength(password)
        if not bcrypt.check_password_hash(user.password_hash, password):
            logger.warning(f"Password verification failed for user {user.email}")
            raise AuthException("Invalid password")
            
        logger.info(f"Password verified successfully for user {user.email}")
        return (True, {}, "Password verified successfully")
        
    except AuthException:
        raise
    except Exception as e:
        logger.error(f"Password verification error for {user.email}: {str(e)}")
        raise AuthException(f"Password verification failed: {str(e)}")
