"""WTForms for search functionality"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import Optional, Length
from app.utils.constants import BRANCHES


class StudentSearchForm(FlaskForm):
    """Search form for students"""
    name = StringField('Name', validators=[
        Optional(),
        Length(max=100)
    ])
    student_id = StringField('Student ID', validators=[
        Optional(),
        Length(max=50)
    ])
    contact = StringField('Contact', validators=[
        Optional(),
        Length(max=15)
    ])
    email = StringField('Email', validators=[
        Optional(),
        Length(max=100)
    ])
    branch = SelectField('Branch', 
        choices=[('', 'All Branches')] + [(b, b) for b in BRANCHES],
        validators=[Optional()]
    )
    graduation_year = IntegerField('Graduation Year', validators=[Optional()])


class CompanySearchForm(FlaskForm):
    """Search form for companies"""
    company_name = StringField('Company Name', validators=[
        Optional(),
        Length(max=200)
    ])
    hr_name = StringField('HR Name', validators=[
        Optional(),
        Length(max=100)
    ])
