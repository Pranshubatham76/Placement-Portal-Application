"""
Celery helper functions for easy task invocation.

This module provides clean, reusable functions to call Celery tasks
without dealing with Flask app context and Celery instance retrieval.
"""

from flask import current_app
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_celery_app():
    """
    Get the Celery instance from the current Flask app.
    
    Returns:
        Celery: The Celery application instance, or None if not available
    """
    try:
        return current_app.extensions.get("celery")
    except RuntimeError:
        # No Flask app context available
        logger.warning("No Flask app context available for Celery")
        return None


def send_email_async(
    subject: str,
    recipients: List[str],
    sender: str,
    body: str,
    countdown: int = 0,
    max_retries: int = 3,
    html: Optional[str] = None,
    **kwargs
) -> Optional[Any]:
    """
    Send an email asynchronously using Celery.
    
    This is a convenience wrapper around the send_email Celery task.
    It handles getting the Celery instance and provides a clean API.
    
    Args:
        subject: Email subject line
        recipients: List of recipient email addresses
        sender: Sender email address
        body: Plain text email body
        countdown: Seconds to wait before sending (default: 0)
        max_retries: Maximum number of retry attempts (default: 3)
        html: Optional HTML version of the email body
        **kwargs: Additional Celery task options
    
    Returns:
        AsyncResult: Celery task result object, or None if Celery unavailable
    
    Example:
        >>> send_email_async(
        ...     subject="Welcome!",
        ...     recipients=["user@example.com"],
        ...     sender="noreply@example.com",
        ...     body="Welcome to our platform!",
        ...     countdown=10
        ... )
    """
    celery_app = get_celery_app()
    
    if not celery_app:
        logger.error("Celery not available, email will not be sent")
        return None
    
    # Default retry policy
    retry_policy = kwargs.pop('retry_policy', {
        'max_retries': max_retries,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    })
    
    try:
        task_result = celery_app.send_task(
            'app.celery_app.tasks.send_email',
            args=[subject, recipients, sender, body],
            countdown=countdown,
            retry=True,
            retry_policy=retry_policy,
            **kwargs
        )
        
        logger.info(f"Email task queued for {recipients} with task_id: {task_result.id}")
        return task_result
        
    except Exception as e:
        logger.error(f"Failed to queue email task: {str(e)}")
        return None


def send_welcome_email(email: str, user_type: str = "student") -> Optional[Any]:
    """
    Send a welcome email to a newly registered user.
    
    Args:
        email: User's email address
        user_type: Type of user ('student' or 'company')
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    """
    from config import Config
    
    messages = {
        "student": "You are successfully registered to Placement Portal. Explore the platform and make the most of your experience. Please login to continue.",
        "company": "You are successfully registered to Placement Portal. Your account is pending admin approval."
    }
    
    return send_email_async(
        subject="Welcome to Placement Portal",
        recipients=[email],
        sender=Config.MAIL_USERNAME,
        body=messages.get(user_type, messages["student"]),
        countdown=10,
        max_retries=3
    )


def send_otp_email(email: str, otp: str) -> Optional[Any]:
    """
    Send an OTP (One-Time Password) email for password reset.
    
    Args:
        email: User's email address
        otp: The OTP code to send
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    """
    from config import Config
    
    return send_email_async(
        subject="Password Reset OTP",
        recipients=[email],
        sender=Config.MAIL_USERNAME,
        body=f"Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.",
        countdown=2,  # Minimal delay for time-sensitive OTP
        max_retries=2  # Fewer retries for OTP
    )


def send_approval_notification(email: str, company_name: str, approved: bool) -> Optional[Any]:
    """
    Send company approval/rejection notification email.
    
    Args:
        email: Company email address
        company_name: Name of the company
        approved: True if approved, False if rejected
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    """
    from config import Config
    
    if approved:
        subject = "Company Registration Approved"
        body = f"Congratulations! Your company '{company_name}' has been approved. You can now login and post job opportunities."
    else:
        subject = "Company Registration Update"
        body = f"We regret to inform you that your company '{company_name}' registration could not be approved at this time. Please contact support for more information."
    
    return send_email_async(
        subject=subject,
        recipients=[email],
        sender=Config.MAIL_USERNAME,
        body=body,
        countdown=5,
        max_retries=3
    )


# Add more helper functions as needed for different email types
def send_application_notification(email: str, job_title: str, company_name: str) -> Optional[Any]:
    """
    Send job application confirmation email to student.
    
    Args:
        email: Student's email address
        job_title: Title of the job applied for
        company_name: Name of the company
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    """
    from config import Config
    
    return send_email_async(
        subject=f"Application Submitted - {job_title}",
        recipients=[email],
        sender=Config.MAIL_USERNAME,
        body=f"Your application for '{job_title}' at {company_name} has been successfully submitted. Good luck!",
        countdown=5,
        max_retries=3
    )


# ============================================
# Periodic Task Helpers (Manual Triggering)
# ============================================

def trigger_daily_report_now() -> Optional[Any]:
    """
    Manually trigger the daily report generation.
    
    Useful for testing or when admin wants an immediate report.
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    
    Example:
        >>> from app.celery_app.helpers import trigger_daily_report_now
        >>> trigger_daily_report_now()
    """
    celery_app = get_celery_app()
    
    if not celery_app:
        logger.error("Celery not available, cannot trigger daily report")
        return None
    
    try:
        task_result = celery_app.send_task(
            'app.celery_app.tasks.send_daily_report'
        )
        logger.info(f"Daily report triggered manually with task_id: {task_result.id}")
        return task_result
    except Exception as e:
        logger.error(f"Failed to trigger daily report: {str(e)}")
        return None


def trigger_weekly_report_now() -> Optional[Any]:
    """
    Manually trigger the weekly report generation.
    
    Useful for testing or when admin wants an immediate report.
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    
    Example:
        >>> from app.celery_app.helpers import trigger_weekly_report_now
        >>> trigger_weekly_report_now()
    """
    celery_app = get_celery_app()
    
    if not celery_app:
        logger.error("Celery not available, cannot trigger weekly report")
        return None
    
    try:
        task_result = celery_app.send_task(
            'app.celery_app.tasks.send_weekly_report'
        )
        logger.info(f"Weekly report triggered manually with task_id: {task_result.id}")
        return task_result
    except Exception as e:
        logger.error(f"Failed to trigger weekly report: {str(e)}")
        return None


def trigger_job_cleanup_now() -> Optional[Any]:
    """
    Manually trigger the expired jobs cleanup.
    
    Useful for testing or immediate cleanup.
    
    Returns:
        AsyncResult: Celery task result, or None if failed
    
    Example:
        >>> from app.celery_app.helpers import trigger_job_cleanup_now
        >>> trigger_job_cleanup_now()
    """
    celery_app = get_celery_app()
    
    if not celery_app:
        logger.error("Celery not available, cannot trigger job cleanup")
        return None
    
    try:
        task_result = celery_app.send_task(
            'app.celery_app.tasks.cleanup_expired_jobs'
        )
        logger.info(f"Job cleanup triggered manually with task_id: {task_result.id}")
        return task_result
    except Exception as e:
        logger.error(f"Failed to trigger job cleanup: {str(e)}")
        return None
