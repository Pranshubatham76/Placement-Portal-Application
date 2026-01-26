"""Role-based access control decorators"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin role for route access
    
    Usage:
        @app.route('/admin/dashboard')
        @login_required
        @admin_required
        def admin_dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def company_required(f):
    """
    Decorator to require company role for route access
    
    Usage:
        @app.route('/company/dashboard')
        @login_required
        @company_required
        def company_dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'company':
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator to require student role for route access
    
    Usage:
        @app.route('/student/dashboard')
        @login_required
        @student_required
        def student_dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'student':
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Flexible decorator to require any of the specified roles
    
    Usage:
        @app.route('/shared-page')
        @login_required
        @role_required('admin', 'company')
        def shared_page():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
