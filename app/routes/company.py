"""Company routes - Company dashboard, drives, and applications"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import company_required
from app.services import company_service, drive_service, application_service, dashboard_service
from app.models.company import Company

# Create Blueprint
company_bp = Blueprint('company', __name__, url_prefix='/company')


@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    """Company dashboard"""
    # Get company profile
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('auth.login'))
    
    company = data.get('company')
    
    # Check approval status
    if company.approval_status == 'pending':
        return render_template('company/pending_approval.html', company=company)
    
    if company.approval_status == 'rejected':
        flash('Your company registration was rejected. Please contact support.', 'danger')
        return render_template('company/pending_approval.html', company=company)
    
    # Get dashboard stats
    stats = dashboard_service.get_company_dashboard_stats(company.id)
    
    return render_template('company/dashboard.html', company=company, stats=stats)


@company_bp.route('/profile')
@login_required
@company_required
def profile():
    """View company profile"""
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.dashboard'))
    
    company = data.get('company')
    return render_template('company/profile.html', company=company)


@company_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_profile():
    """Edit company profile"""
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.dashboard'))
    
    company = data.get('company')
    
    if request.method == 'POST':
        profile_data = {
            'company_name': request.form.get('company_name'),
            'hr_name': request.form.get('hr_name'),
            'hr_email': request.form.get('hr_email'),
            'hr_contact': request.form.get('hr_contact'),
            'address': request.form.get('address'),
            'description': request.form.get('description'),
            'website': request.form.get('website')
        }
        
        success, data, message = company_service.update_company_profile(
            company.id, profile_data, current_user.id
        )
        
        flash(message, 'success' if success else 'danger')
        
        if success:
            return redirect(url_for('company.profile'))
    
    return render_template('company/profile_edit.html', company=company)


@company_bp.route('/drives')
@login_required
@company_required
def list_drives():
    """List all company drives"""
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.dashboard'))
    
    company = data.get('company')
    
    # Get drives
    status_filter = request.args.get('status')
    success, data, message = drive_service.get_company_drives(company.id, status_filter)
    
    drives = data.get('drives', [])
    return render_template('company/drives_list.html', drives=drives, company=company)


@company_bp.route('/drive/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_drive():
    """Create new placement drive"""
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.dashboard'))
    
    company = data.get('company')
    
    if request.method == 'POST':
        drive_data = {
            'job_title': request.form.get('job_title'),
            'job_description': request.form.get('job_description'),
            'job_location': request.form.get('job_location'),
            'job_type': request.form.get('job_type'),
            'min_cgpa': float(request.form.get('min_cgpa', 0)),
            'eligible_branches': ','.join(request.form.getlist('eligible_branches')),
            'eligible_years': request.form.get('eligible_years'),
            'ctc': int(request.form.get('ctc', 0)),
            'deadline': request.form.get('deadline'),
            'drive_date': request.form.get('drive_date') or None,
            'max_applicants': int(request.form.get('max_applicants', 0)) if request.form.get('max_applicants') else None
        }
        
        success, data, message = drive_service.create_drive(company.id, drive_data)
        
        flash(message, 'success' if success else 'danger')
        
        if success:
            return redirect(url_for('company.list_drives'))
    
    return render_template('company/drive_create.html', company=company)


@company_bp.route('/drive/<int:drive_id>')
@login_required
@company_required
def view_drive(drive_id):
    """View drive details"""
    success, data, message = drive_service.get_drive_by_id(drive_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.list_drives'))
    
    drive = data.get('drive')
    
    # Get applications count
    success, app_data, _ = application_service.get_drive_applications(drive_id)
    applications_count = len(app_data.get('applications', []))
    
    return render_template('company/drive_detail.html', drive=drive, applications_count=applications_count)


@company_bp.route('/drive/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(drive_id):
    """Edit placement drive"""
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.dashboard'))
    
    company = data.get('company')
    
    success, data, message = drive_service.get_drive_by_id(drive_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.list_drives'))
    
    drive = data.get('drive')
    
    # Verify ownership
    if drive.company_id != company.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('company.list_drives'))
    
    if request.method == 'POST':
        drive_data = {
            'job_title': request.form.get('job_title'),
            'job_description': request.form.get('job_description'),
            'job_location': request.form.get('job_location'),
            'job_type': request.form.get('job_type'),
            'min_cgpa': float(request.form.get('min_cgpa', 0)),
            'eligible_branches': ','.join(request.form.getlist('eligible_branches')),
            'eligible_years': request.form.get('eligible_years'),
            'ctc': int(request.form.get('ctc', 0)),
            'deadline': request.form.get('deadline'),
            'drive_date': request.form.get('drive_date') or None,
            'max_applicants': int(request.form.get('max_applicants', 0)) if request.form.get('max_applicants') else None
        }
        
        success, data, message = drive_service.update_drive(drive_id, drive_data, company.id)
        
        flash(message, 'success' if success else 'danger')
        
        if success:
            return redirect(url_for('company.view_drive', drive_id=drive_id))
    
    return render_template('company/drive_edit.html', drive=drive, company=company)


@company_bp.route('/drive/<int:drive_id>/close', methods=['POST'])
@login_required
@company_required
def close_drive(drive_id):
    """Close placement drive"""
    success, data, message = company_service.get_company_by_user_id(current_user.id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.dashboard'))
    
    company = data.get('company')
    
    success, data, message = drive_service.close_drive(drive_id, company.id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('company.view_drive', drive_id=drive_id))


@company_bp.route('/drive/<int:drive_id>/applications')
@login_required
@company_required
def view_applications(drive_id):
    """View applications for a drive"""
    # Verify ownership
    success, data, message = drive_service.get_drive_by_id(drive_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('company.list_drives'))
    
    drive = data.get('drive')
    
    # Get applications
    status_filter = request.args.get('status')
    success, data, message = application_service.get_drive_applications(drive_id, status_filter)
    
    applications = data.get('applications', [])
    
    return render_template('company/applications_list.html', applications=applications, drive=drive)


@company_bp.route('/application/<int:application_id>')
@login_required
@company_required
def view_application(application_id):
    """View application details"""
    from app.models.application import Application
    
    application = Application.query.get_or_404(application_id)
    
    return render_template('company/application_detail.html', application=application)


@company_bp.route('/application/<int:application_id>/update-status', methods=['POST'])
@login_required
@company_required
def update_application_status(application_id):
    """Update application status"""
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    success, data, message = application_service.update_application_status(
        application_id, new_status, current_user.id, notes
    )
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('company.view_application', application_id=application_id))
