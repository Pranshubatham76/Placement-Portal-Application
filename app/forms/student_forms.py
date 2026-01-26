"""WTForms for student profile management"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from app.utils.constants import BRANCHES


class StudentProfileForm(FlaskForm):
    """Student profile form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    student_id = StringField('Student ID', validators=[
        DataRequired(message='Student ID is required'),
        Length(min=3, max=50, message='Student ID must be between 3 and 50 characters')
    ])
    contact = StringField('Contact Number', validators=[
        DataRequired(message='Contact number is required'),
        Length(min=10, max=15, message='Invalid contact number')
    ])
    branch = SelectField('Branch', choices=[(b, b) for b in BRANCHES], validators=[
        DataRequired(message='Branch is required')
    ])
    cgpa = DecimalField('CGPA', validators=[
        DataRequired(message='CGPA is required'),
        NumberRange(min=0.0, max=10.0, message='CGPA must be between 0.0 and 10.0')
    ], places=2)
    graduation_year = IntegerField('Graduation Year', validators=[
        DataRequired(message='Graduation year is required'),
        NumberRange(min=2020, max=2030, message='Invalid graduation year')
    ])
    skills = TextAreaField('Skills (comma-separated)', validators=[
        Length(max=500, message='Skills list too long')
    ])
    address = TextAreaField('Address', validators=[
        Length(max=500, message='Address too long')
    ])

    linkedin_url = StringField('LinkedIn URL', validators=[
        Length(max=200, message='LinkedIn URL too long')
    ])
    github_url = StringField('GitHub URL', validators=[
        Length(max=200, message='GitHub URL too long')
    ])
    
    resume = FileField('Resume', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, and DOCX files allowed'),
        Optional()
    ])


# class ResumeUploadForm(FlaskForm):
#     """Resume upload form"""
#     resume = FileField('Upload Resume', validators=[
#         DataRequired(message='Please select a file'),
#         FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, and DOCX files allowed')
#     ])
