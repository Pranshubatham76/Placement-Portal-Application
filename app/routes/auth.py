"""Authentication routes - User login, registration, password reset"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required, confirm_login
from app.services.auth_service import (
    register_user,
    register_company,
    authenticate_user,
    logout_user_service,
    generate_password_reset_otp,
    reset_password_with_otp,
    verify_password
)
from app.utils.exceptions import AuthException

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle student registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Call the service function
            success, data, message = register_user(email, password)
            flash(message, 'success')
            return redirect(url_for('auth.login'))
            
        except AuthException as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('auth.register'))
    
    # Render registration form for GET request
    return render_template('auth/student_registration.html')


@auth_bp.route('/company/register', methods=['GET', 'POST'])
def register_company_route():
    """Handle company registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Get company data
        company_data = {
            'company_name': request.form.get('company_name'),
            'hr_name': request.form.get('hr_name'),
            'hr_email': request.form.get('hr_email'),
            'hr_contact': request.form.get('hr_contact'),
            'address': request.form.get('address', ''),
            'description': request.form.get('description', ''),
            'website': request.form.get('website', '')
        }
        
        try:
            # Call the service function
            success, data, message = register_company(email, password, company_data)
            flash(message, 'info')
            return redirect(url_for('auth.login'))
            
        except AuthException as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.register_company_route'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('auth.register_company_route'))
    
    # Render registration form for GET request
    return render_template('auth/company_register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember', False))
        
        try:
            # Call the service function
            data = authenticate_user(email, password, remember)
            
            flash(data.get('message', 'Login successful'), 'success')
            # Get next route from data
            next_route = data.get('next_route', 'index')
            # Check if there's a next parameter
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for(next_route))
            
        except AuthException as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('auth.login'))
    
    # Render login form for GET request
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    try:
        success, data, message = logout_user_service()
        flash(message, 'success')
    except AuthException as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash("An error occurred during logout.", 'danger')
        
    return redirect(url_for('auth.login'))


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password_route():
    """Handle forget password - send OTP"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        try:
            # Call the service function
            success, data, message = generate_password_reset_otp(email)
            
            # Store OTP and email in session
            session['password_reset_otp'] = data['otp']
            session['password_reset_email'] = data['email']
            flash(message, 'success')
            return redirect(url_for('auth.reset_password_route'))
            
        except AuthException as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.forget_password_route'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('auth.forget_password_route'))
    
    return render_template('auth/forget_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_route():
    """Handle password reset with OTP"""
    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('new_password')
        
        # Get session data
        session_otp = session.get('password_reset_otp')
        email = session.get('password_reset_email')
        
        try:
            # Call the service function
            success, data, message = reset_password_with_otp(email, otp, session_otp, new_password)
            
            # Clear session
            session.pop('password_reset_otp', None)
            session.pop('password_reset_email', None)
            flash(message, 'success')
            return redirect(url_for('auth.login'))
            
        except AuthException as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.reset_password_route'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('auth.reset_password_route'))
    
    # Check if OTP was generated
    if 'password_reset_otp' not in session:
        flash('Please request a password reset first', 'warning')
        return redirect(url_for('auth.forget_password_route'))
    
    return render_template('auth/reset_password.html')


@auth_bp.route('/reauthenticate', methods=['GET', 'POST'])
@login_required
def reauthenticate():
    """Handle re-authentication for sensitive operations"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        if not password:
            flash('Password is required', 'danger')
            return redirect(url_for('auth.reauthenticate'))
        
        try:
            # Verify password using service
            success, data, message = verify_password(current_user, password)
            
            # Confirm fresh login
            confirm_login()
            flash('Re-authentication successful', 'success')
            return redirect(request.args.get('next') or url_for('index'))
            
        except AuthException as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.reauthenticate'))
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", 'danger')
            return redirect(url_for('auth.reauthenticate'))
    
    return render_template('auth/reauthenticate.html')
