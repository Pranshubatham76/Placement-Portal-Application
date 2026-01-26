from app import db
from datetime import datetime

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    job_location = db.Column(db.String(200), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    min_cgpa = db.Column(db.Float, nullable=False)
    eligible_branches = db.Column(db.Text, nullable=False)
    eligible_years = db.Column(db.String(50), nullable=False)
    ctc_min = db.Column(db.Float, nullable=True)
    ctc_max = db.Column(db.Float, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime, nullable=True)
    max_applicants = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    approved_by = db.Column(db.Integer, db.ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship("Company", backref=db.backref("placement_drives", lazy=True))
    admin = db.relationship("Admin", backref=db.backref("approved_drives", lazy=True))
    
    @property
    def ctc(self):
        return self.ctc_min

    @property
    def deadline(self):
        return self.application_deadline

    def __repr__(self):
        return f'<PlacementDrive {self.job_title}>'

    # Indexes
    __table_args__ = (
       db.Index('idx_drives_company', 'company_id'),
       db.Index('idx_drives_status', 'status'),
       db.Index('idx_drives_deadline', 'application_deadline'),
       db.Index('idx_drives_approved', 'status', 'approved_at'),
    )
    