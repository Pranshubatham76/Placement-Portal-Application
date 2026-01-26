"""WTForms for applications"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length


class ApplicationForm(FlaskForm):
    """Application submission form"""
    drive_id = HiddenField('Drive ID', validators=[
        DataRequired()
    ])
    cover_letter = TextAreaField('Cover Letter (Optional)', validators=[
        Optional(),
        Length(max=1000, message='Cover letter too long')
    ])
