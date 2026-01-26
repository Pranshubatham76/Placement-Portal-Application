from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    hr_name = db.Column(db.String(100), nullable=False)
    hr_email = db.Column(db.String(120), nullable=False, unique=True)
    hr_contact = db.Column(db.String(20), nullable=False, unique=True)
    website = db.Column(db.String(200), nullable=True, unique=True)
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    approval_status = db.Column(db.String(20), nullable=False, default="pending")
    approved_by = db.Column(db.Integer, db.ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("company", uselist=False), lazy=True)
    admin = db.relationship("Admin", foreign_keys=[approved_by], backref=db.backref("approved_companies", lazy=True))
    
    __table_args__ = (
        db.Index('idx_companies_id', "id"),
        db.Index('idx_companies_name', 'company_name'),
        db.Index('idx_companies_approval', 'approval_status'),
    )
    
    def __repr__(self):
        return f'<Company {self.company_name}>'
