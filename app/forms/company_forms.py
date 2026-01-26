"""WTForms for company profile management"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class CompanyProfileForm(FlaskForm):
    """Company profile edit form"""
    company_name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required'),
        Length(min=2, max=200, message='Company name must be between 2 and 200 characters')
    ])
    hr_name = StringField('HR Name', validators=[
        DataRequired(message='HR name is required'),
        Length(min=2, max=100, message='HR name must be between 2 and 100 characters')
    ])
    hr_email = StringField('HR Email', validators=[
        DataRequired(message='HR email is required'),
        Email(message='Invalid email address')
    ])
    hr_contact = StringField('HR Contact', validators=[
        DataRequired(message='HR contact is required'),
        Length(min=10, max=15, message='Invalid contact number')
    ])
    address = TextAreaField('Address', validators=[
        Optional(),
        Length(max=500, message='Address too long')
    ])
    description = TextAreaField('Company Description', validators=[
        Optional(),
        Length(max=1000, message='Description too long')
    ])
    website = StringField('Website', validators=[
        Optional(),
        Length(max=200, message='Website URL too long')
    ])
