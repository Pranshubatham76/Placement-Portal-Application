from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.admin_service_route import delete_company, edit_company_info

# Create Blueprint
admin_service = Blueprint('admin_service', __name__,'/admin')

@admin_service.route('/delete_company/<int:id>', methods=['DELETE'])
def remove_company(id):
    delete_company(id)
    