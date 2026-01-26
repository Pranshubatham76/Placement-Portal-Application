"""WTForms for placement drive management"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app.utils.constants import JOB_TYPES, BRANCHES


class PlacementDriveForm(FlaskForm):
    """Placement drive creation/edit form"""
    job_title = StringField('Job Title', validators=[
        DataRequired(message='Job title is required'),
        Length(min=3, max=200, message='Job title must be between 3 and 200 characters')
    ])
    job_description = TextAreaField('Job Description', validators=[
        DataRequired(message='Job description is required'),
        Length(min=10, max=2000, message='Description must be between 10 and 2000 characters')
    ])
    job_location = StringField('Job Location', validators=[
        DataRequired(message='Job location is required'),
        Length(min=2, max=200, message='Location must be between 2 and 200 characters')
    ])
    job_type = SelectField('Job Type', choices=[(jt, jt.title()) for jt in JOB_TYPES], validators=[
        DataRequired(message='Job type is required')
    ])
    min_cgpa = DecimalField('Minimum CGPA', validators=[
        DataRequired(message='Minimum CGPA is required'),
        NumberRange(min=0.0, max=10.0, message='CGPA must be between 0.0 and 10.0')
    ], places=2)
    eligible_branches = SelectMultipleField('Eligible Branches', 
        choices=[(b, b) for b in BRANCHES],
        validators=[DataRequired(message='At least one branch must be selected')]
    )
    eligible_years = StringField('Eligible Graduation Years (comma-separated)', validators=[
        DataRequired(message='Eligible years are required'),
        Length(max=50, message='Years list too long')
    ])
    ctc = IntegerField('CTC (Annual in INR)', validators=[
        DataRequired(message='CTC is required'),
        NumberRange(min=0, message='CTC must be positive')
    ])
    deadline = DateField('Application Deadline', format='%Y-%m-%d', validators=[
        DataRequired(message='Deadline is required')
    ])
    drive_date = DateField('Drive Date', format='%Y-%m-%d', validators=[
        Optional()
    ])
    max_applicants = IntegerField('Maximum Applicants', validators=[
        Optional(),
        NumberRange(min=1, message='Must allow at least 1 applicant')
    ])
