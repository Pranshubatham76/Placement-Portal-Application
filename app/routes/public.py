"""Public routes - Landing page, about, contact"""

from flask import Blueprint, render_template

# Create Blueprint
public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@public_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@public_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')
