from app import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=False)
    application_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="applied") # 'applied', 'shortlisted', 'selected', 'rejected'
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    student = db.relationship("Student", backref=db.backref("applications", lazy=True))
    drive = db.relationship("PlacementDrive", backref=db.backref("applications", lazy=True))
    company = db.relationship("Company", foreign_keys=[updated_by], backref=db.backref("updated_applications", lazy=True))
    
    # Indexes and constraints
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
        db.Index('idx_applications_student', 'student_id'),
        db.Index('idx_applications_drive', 'drive_id'),
        db.Index('idx_applications_status', 'status'),
        db.Index('idx_applications_unique', 'student_id', 'drive_id', unique=True),
    )
    
    def __repr__(self):
        return f'<Application Student:{self.student_id} Drive:{self.drive_id}>'
