"""WTForms for authentication (login, registration)"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    """Login form for all users"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember = BooleanField('Remember Me')


class StudentRegisterForm(FlaskForm):
    """Student registration form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')


class CompanyRegisterForm(FlaskForm):
    """Company registration form"""
    # User credentials
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    # Company details
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
        Length(max=500, message='Address too long')
    ])
    description = TextAreaField('Company Description', validators=[
        Length(max=1000, message='Description too long')
    ])
    website = StringField('Website', validators=[
        Length(max=200, message='Website URL too long')
    ])
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')


class ForgetPasswordForm(FlaskForm):
    """Forget password form - request OTP"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])


class ResetPasswordForm(FlaskForm):
    """Reset password form with OTP"""
    otp = StringField('OTP', validators=[
        DataRequired(message='OTP is required'),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('new_password', message='Passwords must match')
    ])
