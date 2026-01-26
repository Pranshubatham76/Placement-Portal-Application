"""Student routes - Student dashboard, profile, drives, and applications"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import student_required
from app.services import student_service, file_service, application_service, dashboard_service, drive_service
from app.models.student import Student
from app.utils.exceptions import StudentException
from app.forms.student_forms import StudentProfileForm

# Create Blueprint
student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    # Get student profile
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException:
        # No profile yet, redirect to create
        flash('Please complete your profile first', 'info')
        return redirect(url_for('student.edit_profile'))
    
    # Get dashboard stats
    stats = dashboard_service.get_student_dashboard_stats(student.id)
    
    # Get recent drives
    try:
        _, data, _ = student_service.get_eligible_drives(student.id)
        recent_drives = data.get('drives', [])[:5]  # Latest 5
    except StudentException:
        recent_drives = []
    
    return render_template('student/dashboard.html', student=student, stats=stats, recent_drives=recent_drives)


@student_bp.route('/profile')
@login_required
@student_required
def profile():
    """View student profile"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.edit_profile'))
    return render_template('student/profile.html', student=student)


@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@student_required
def edit_profile():
    """Edit student profile"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException:
        student = None
    
    form = StudentProfileForm()
    
    if request.method == 'GET' and student:
        # Pre-populate form
        form.full_name.data = student.name
        form.student_id.data = student.student_id
        form.contact.data = student.contact
        form.branch.data = student.branch
        form.cgpa.data = student.cgpa
        form.graduation_year.data = student.graduation_year
        form.skills.data = student.skills
        form.address.data = student.address
        form.linkedin_url.data = student.linkedin_url
        form.github_url.data = student.github_url

    if form.validate_on_submit():
        profile_data = {
            'full_name': form.full_name.data,
            'student_id': form.student_id.data,
            'contact': form.contact.data,
            'branch': form.branch.data,
            'cgpa': float(form.cgpa.data),
            'graduation_year': int(form.graduation_year.data),
            'skills': form.skills.data,
            'address': form.address.data,
            'linkedin_url': form.linkedin_url.data,
            'github_url': form.github_url.data,
            'resume': form.resume.data
        }
        
        try:
            if student:
                success, data, message = student_service.update_student_profile(student.id, profile_data)
                
                # Handle resume upload if provided
                if form.resume.data:
                    file_service.upload_resume(student.id, form.resume.data)
                    
            else:
                success, data, message = student_service.create_student_profile(current_user.id, profile_data)
                # Resume upload is handled inside create_student_profile if passed as 'resume_path'? 
                # No, student_service.create takes 'resume_path' string, not file object.
                # We need to handle file upload separately or update service to handle file object.
                # Looking at student_service.create_student_profile, it expects 'resume_path'. 
                # Let's fix this logic: create profile first, then upload resume if needed.
                
                if success and form.resume.data:
                    new_student = data.get('student')
                    file_service.upload_resume(new_student.id, form.resume.data)

            flash('Profile updated successfully', 'success')
            return redirect(url_for('student.profile'))
            
        except StudentException as e:
            flash(str(e), 'danger')
        except Exception as e:
             # Catch file upload errors or others
             flash(f"An error occurred: {str(e)}", 'danger')

    return render_template('student/profile_edit.html', student=student, form=form)


@student_bp.route('/resume/upload', methods=['POST'])
@login_required
@student_required
def upload_resume():
    """Upload resume"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    if 'resume' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('student.edit_profile'))
    
    file = request.files['resume']
    
    success, data, message = file_service.upload_resume(student.id, file)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('student.edit_profile'))


@student_bp.route('/resume/delete', methods=['POST'])
@login_required
@student_required
def delete_resume():
    """Delete resume"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    success, data, message = file_service.delete_resume(student.id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('student.edit_profile'))


@student_bp.route('/drives')
@login_required
@student_required
def list_drives():
    """List all available drives"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get all approved drives
    from app.models.placement_drive import PlacementDrive
    from datetime import datetime
    
    drives = PlacementDrive.query.filter_by(status='approved').filter(
        PlacementDrive.deadline >= datetime.utcnow()
    ).all()
    
    return render_template('student/drives_list.html', drives=drives, student=student)


@student_bp.route('/drive/<int:drive_id>')
@login_required
@student_required
def view_drive(drive_id):
    """View drive details"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    success, data, message = drive_service.get_drive_by_id(drive_id)
    
    if not success:
        flash(message, 'danger')
        return redirect(url_for('student.list_drives'))
    
    drive = data.get('drive')
    
    # Check eligibility
    from app.utils.validators import check_eligibility
    is_eligible, reasons = check_eligibility(student, drive)
    
    # Check if already applied
    from app.models.application import Application
    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()
    
    return render_template('student/drive_detail.html', 
                         drive=drive, 
                         student=student,
                         is_eligible=is_eligible,
                         ineligibility_reasons=reasons,
                         already_applied=existing_application is not None)


@student_bp.route('/drive/<int:drive_id>/apply', methods=['POST'])
@login_required
@student_required
def apply_to_drive(drive_id):
    """Apply to placement drive"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    success, data, message = application_service.apply_to_drive(student.id, drive_id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('student.view_drive', drive_id=drive_id))


@student_bp.route('/applications')
@login_required
@student_required
def list_applications():
    """List student applications"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get applications
    status_filter = request.args.get('status')
    success, data, message = application_service.get_student_applications(student.id, status_filter)
    
    applications = data.get('applications', [])
    
    return render_template('student/applications_list.html', applications=applications, student=student)


@student_bp.route('/application/<int:application_id>')
@login_required
@student_required
def view_application(application_id):
    """View application details"""
    from app.models.application import Application
    
    application = Application.query.get_or_404(application_id)
    
    # Verify ownership
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
        if application.student_id != student.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('student.list_applications'))
    except StudentException:
        flash('Student profile not found', 'danger')
        return redirect(url_for('student.dashboard'))
    
    return render_template('student/application_detail.html', application=application)


@student_bp.route('/application/<int:application_id>/withdraw', methods=['POST'])
@login_required
@student_required
def withdraw_application(application_id):
    """Withdraw application"""
    try:
        _, data, _ = student_service.get_student_by_user_id(current_user.id)
        student = data.get('student')
    except StudentException as e:
        flash(str(e), 'danger')
        return redirect(url_for('student.dashboard'))
    
    success, data, message = application_service.withdraw_application(application_id, student.id)
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('student.list_applications'))
