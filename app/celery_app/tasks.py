from flask_mail import Message
from app import mail, db
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def send_email(subject, recipients, sender, body):
    """
    Send email asynchronously using Celery
    
    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        sender (str): Sender email address
        body (str): Email body content
    
    Returns:
        dict: Status of email sending operation
    """
    try:
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = body
        mail.send(msg)
        logger.info(f"Email sent successfully to {recipients}")
        return {"status": "success", "recipients": recipients}
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {str(e)}")
        raise


def send_daily_report():
    """
    Periodic task: Generate and send daily report to admin
    
    This task runs automatically every day at a scheduled time.
    It collects statistics from the last 24 hours and emails them to admins.
    
    Returns:
        dict: Report generation status
    """
    try:
        from app.models.user import User
        from app.models.student import Student
        from app.models.company import Company
        from app.models.job import Job
        from app.models.application import Application
        from config import Config
        
        logger.info("Starting daily report generation...")
        
        # Calculate date range (last 24 hours)
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Collect statistics
        new_students = Student.query.filter(Student.created_at >= yesterday).count()
        new_companies = Company.query.filter(Company.created_at >= yesterday).count()
        new_jobs = Job.query.filter(Job.created_at >= yesterday).count()
        new_applications = Application.query.filter(Application.created_at >= yesterday).count()
        pending_companies = Company.query.filter_by(approval_status='pending').count()
        
        # Generate report content
        report_body = f"""
Daily Placement Portal Report
Generated on: {today.strftime('%Y-%m-%d %H:%M:%S')}

=== Statistics for Last 24 Hours ===

New Registrations:
- Students: {new_students}
- Companies: {new_companies}

Job Postings:
- New Jobs Posted: {new_jobs}
- Total Applications: {new_applications}

Pending Actions:
- Companies Awaiting Approval: {pending_companies}

---
This is an automated report from Placement Portal.
"""
        
        # Get admin emails
        admin_users = User.query.filter_by(role='admin').all()
        admin_emails = [admin.email for admin in admin_users]
        
        if admin_emails:
            # Send email to all admins
            msg = Message(
                subject=f"Daily Report - {today.strftime('%Y-%m-%d')}",
                sender=Config.MAIL_USERNAME,
                recipients=admin_emails,
                body=report_body
            )
            mail.send(msg)
            logger.info(f"Daily report sent to {len(admin_emails)} admins")
            return {"status": "success", "recipients": len(admin_emails)}
        else:
            logger.warning("No admin users found to send daily report")
            return {"status": "no_recipients"}
            
    except Exception as e:
        logger.error(f"Failed to generate daily report: {str(e)}")
        raise


def send_weekly_report():
    """
    Periodic task: Generate and send weekly report to admin
    
    This task runs automatically every week (e.g., Monday at 9 AM).
    It provides a comprehensive overview of the week's activities.
    
    Returns:
        dict: Report generation status
    """
    try:
        from app.models.user import User
        from app.models.student import Student
        from app.models.company import Company
        from app.models.job import Job
        from app.models.application import Application
        from config import Config
        
        logger.info("Starting weekly report generation...")
        
        # Calculate date range (last 7 days)
        today = datetime.now()
        last_week = today - timedelta(days=7)
        
        # Collect statistics
        new_students = Student.query.filter(Student.created_at >= last_week).count()
        new_companies = Company.query.filter(Company.created_at >= last_week).count()
        approved_companies = Company.query.filter(
            Company.approval_status == 'approved',
            Company.approved_at >= last_week
        ).count()
        new_jobs = Job.query.filter(Job.created_at >= last_week).count()
        new_applications = Application.query.filter(Application.created_at >= last_week).count()
        
        # Total counts
        total_students = Student.query.count()
        total_companies = Company.query.filter_by(approval_status='approved').count()
        total_jobs = Job.query.filter_by(status='active').count()
        
        # Generate report content
        report_body = f"""
Weekly Placement Portal Report
Week Ending: {today.strftime('%Y-%m-%d')}
Report Period: {last_week.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}

=== Weekly Activity Summary ===

New Registrations (Last 7 Days):
- Students: {new_students}
- Companies: {new_companies}
- Companies Approved: {approved_companies}

Job Market Activity:
- New Jobs Posted: {new_jobs}
- Total Applications Received: {new_applications}

=== Overall Platform Statistics ===

Total Active Users:
- Students: {total_students}
- Companies: {total_companies}
- Active Job Postings: {total_jobs}

---
This is an automated weekly report from Placement Portal.
For detailed analytics, please login to the admin dashboard.
"""
        
        # Get admin emails
        admin_users = User.query.filter_by(role='admin').all()
        admin_emails = [admin.email for admin in admin_users]
        
        if admin_emails:
            # Send email to all admins
            msg = Message(
                subject=f"Weekly Report - Week of {today.strftime('%Y-%m-%d')}",
                sender=Config.MAIL_USERNAME,
                recipients=admin_emails,
                body=report_body
            )
            mail.send(msg)
            logger.info(f"Weekly report sent to {len(admin_emails)} admins")
            return {"status": "success", "recipients": len(admin_emails)}
        else:
            logger.warning("No admin users found to send weekly report")
            return {"status": "no_recipients"}
            
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {str(e)}")
        raise

def cleanup_expired_jobs():
    """
    Periodic task: Clean up expired job postings
    
    This task runs daily to mark jobs as expired if their deadline has passed.
    
    Returns:
        dict: Cleanup status
    """
    try:
        from app.models.job import Job
        
        logger.info("Starting expired jobs cleanup...")
        
        today = datetime.now().date()
        
        # Find and update expired jobs
        expired_jobs = Job.query.filter(
            Job.deadline < today,
            Job.status == 'active'
        ).all()
        
        count = 0
        for job in expired_jobs:
            job.status = 'expired'
            count += 1
        
        if count > 0:
            db.session.commit()
            logger.info(f"Marked {count} jobs as expired")
        else:
            logger.info("No expired jobs found")
        
        return {"status": "success", "expired_count": count}
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to cleanup expired jobs: {str(e)}")
        raise


# def send():
#     logger.info("SCHEDULED TASK TRIGGERED: 'send' function is running!")
#     print("SCHEDULED TASK TRIGGERED: 'send' function is running!")
#     return "Schedule task is running"