"""Admin routes - Admin panel for managing the placement portal"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.decorators import admin_required
from app.services import admin_service, drive_service
from app.utils.helpers import paginate_query
import logging
# Create Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

logger = logging.getLogger(__name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    success, data, message = admin_service.get_dashboard_stats()
    
    if not success:
        flash(message, 'danger')
        return render_template('admin/dashboard.html', stats={})
    
    return render_template('admin/dashboard.html', stats=data)


@admin_bp.route('/companies')
@login_required
@admin_required
def list_companies():
    """List all companies with filters"""
    approval_status = request.args.get('status', None)
    
    filters = {}
    if approval_status:
        filters['approval_status'] = approval_status
    
    success, data, message = admin_service.get_all_companies(filters)
    
    if not success:
        flash(message, 'danger')
    
    companies = data.get('companies', [])
    return render_template('admin/companies_list.html', companies=companies)


@admin_bp.route('/companies/pending')
@login_required
@admin_required
def pending_companies():
    """List pending company approvals"""
    filters = {'approval_status': 'pending'}
    success, data, message = admin_service.get_all_companies(filters)
    
    companies = data.get('companies', [])
    return render_template('admin/companies_pending.html', companies=companies)


@admin_bp.route('/company/<int:company_id>')
@login_required
@admin_required
def view_company(company_id):
    """View company details"""
    success, data, message = admin_service.get_company_by_id(company_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('admin.list_companies'))
    
    company = data.get('company')
    return render_template('admin/company_detail.html', company=company)


@admin_bp.route('/company/<int:company_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_company(company_id):
    """Approve a company registration"""
    success, data, message = admin_service.approve_company(company_id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.pending_companies'))


@admin_bp.route('/company/<int:company_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_company(company_id):
    """Reject a company registration"""
    reason = request.form.get('reason', '')
    
    success, data, message = admin_service.reject_company(company_id, reason)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.pending_companies'))


@admin_bp.route('/company/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_company(company_id):
    """Edit company information"""
    if request.method == 'POST':
        company_data = {
            'company_name': request.form.get('company_name'),
            'hr_name': request.form.get('hr_name'),
            'hr_email': request.form.get('hr_email'),
            'hr_contact': request.form.get('hr_contact'),
            'address': request.form.get('address'),
            'description': request.form.get('description'),
            'website': request.form.get('website')
        }
        
        success, data, message = admin_service.update_company(company_id, company_data)
        
        flash(message, 'success' if success else 'danger')
        
        if success:
            return redirect(url_for('admin.view_company', company_id=company_id))
        else:
            return redirect(url_for('admin.edit_company', company_id=company_id))
    
    # GET request - show edit form
    success, data, message = admin_service.get_company_by_id(company_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('admin.list_companies'))
    
    company = data.get('company')
    return render_template('admin/company_edit.html', company=company)


@admin_bp.route('/company/<int:company_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(company_id):
    """Delete a company"""
    success, data, message = admin_service.delete_company(company_id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.list_companies'))


@admin_bp.route('/students')
@login_required
@admin_required
def list_students():
    """List all students with filters"""
    branch = request.args.get('branch', None)
    year = request.args.get('year', None)
    
    filters = {}
    if branch:
        filters['branch'] = branch
    if year:
        try:
            filters['graduation_year'] = int(year)
        except ValueError:
            pass
    
    success, data, message = admin_service.get_all_students(filters)
    
    if not success:
        flash(message, 'danger')
    
    students = data.get('students', [])
    return render_template('admin/students_list.html', students=students)


@admin_bp.route('/student/<int:student_id>')
@login_required
@admin_required
def view_student(student_id):
    """View student details"""
    success, data, message = admin_service.get_student_by_id(student_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('admin.list_students'))
    
    student = data.get('student')
    return render_template('admin/student_detail.html', student=student)


@admin_bp.route('/drives/pending')
@login_required
@admin_required
def pending_drives():
    """List pending drive approvals"""
    # This will be implemented with drive_service
    try:
        success, data, message = drive_service.get_all_drives(filters={'status': 'pending'})
        
        if not success:
            flash(message, 'danger')
            return redirect(url_for('admin.dashboard'))
            
        placement_drives = data.get('drives', [])
        logger.info(f"Retrieved {len(placement_drives)} drives successfully")
        return render_template('admin/drives_list.html', drives=placement_drives)

    except Exception as e:
        logger.error(f"Failed to fetch drives: {str(e)}")
        flash("An error occurred while fetching drives.", "danger")
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/drive/<int:drive_id>')
@login_required
@admin_required
def view_drive(drive_id):
    """View placement drive details"""
    success, data, message = drive_service.get_drive_by_id(drive_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('admin.list_drives_admin'))
    
    drive = data.get('drive')
    
    # Get applications for this drive
    from app.services import application_service
    _, app_data, _ = application_service.get_drive_applications(drive_id)
    applications = app_data.get('applications', [])
    
    return render_template('admin/drive_detail.html', drive=drive, applications=applications)


@admin_bp.route('/drive/<int:drive_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_drive(drive_id):
    """Approve a placement drive"""
    success, data, message = admin_service.approve_drive(drive_id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.pending_drives'))


@admin_bp.route('/drive/<int:drive_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_drive(drive_id):
    """Reject a placement drive"""
    reason = request.form.get('reason', '')
    
    success, data, message = admin_service.reject_drive(drive_id, reason)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.pending_drives'))

@admin_bp.route('/all_drives') # Changed to plural for consistency
@login_required
@admin_required
def list_drives_admin():
    """List all placement drives for admin"""
    try:
        success, data, message = drive_service.get_all_drives()
        
        if not success:
            flash(message, 'danger')
            return redirect(url_for('admin.dashboard'))
            
        placement_drives = data.get('drives', [])
        logger.info(f"Retrieved {len(placement_drives)} drives successfully")
        return render_template('admin/drives_list.html', drives=placement_drives)

    except Exception as e:
        logger.error(f"Failed to fetch drives: {str(e)}")
        flash("An error occurred while fetching drives.", "danger")
        return redirect(url_for('admin.dashboard'))
@admin_bp.route('/drive/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_drive(drive_id):
    """Edit placement drive (admin)"""
    success, data, message = drive_service.get_drive_by_id(drive_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('admin.list_drives_admin'))
    
    drive = data.get('drive')
    
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
        
        success, data, message = drive_service.update_drive(drive_id, drive_data)
        
        flash(message, 'success' if success else 'danger')
        
        if success:
            return redirect(url_for('admin.view_drive', drive_id=drive_id))
            
    return render_template('admin/drive_edit.html', drive=drive)


@admin_bp.route('/drive/<int:drive_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_drive(drive_id):
    """Delete placement drive (admin)"""
    success, data, message = drive_service.delete_drive(drive_id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.list_drives_admin'))
