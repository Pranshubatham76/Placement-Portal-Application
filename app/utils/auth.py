from flask_login import current_user
from functools import wraps
from flask import abort

def role_required(*roles):
    """Decorator to require specific roles"""
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            if current_user.is_blacklisted:
                abort(403, "Your account has been blacklisted")
            if not current_user.is_active:
                abort(403, "Your account is not active")
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'company':
            abort(403)
        if current_user.is_blacklisted:
            flash('Your account has been blacklisted.')
            return redirect(url_for('auth.logout'))
        # Additional check for company approval
        company = Company.query.filter_by(user_id=current_user.id).first()
        if company.approval_status != 'approved':
            flash('Your company is not yet approved.')
            return redirect(url_for('company.pending_approval'))
        return f(*args, **kwargs)
    return decorated_function
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'student':
            abort(403)
        if current_user.is_blacklisted:
            flash('Your account has been blacklisted.')
            return redirect(url_for('auth.logout'))
        return f(*args, **kwargs)
    return decorated_function