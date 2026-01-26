from app import db

class Student(db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False, unique=True)
    branch = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    resume_path = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True, unique=True)
    github_url = db.Column(db.String(500), nullable=True, unique=True)
    skills = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Relationship
    user = db.relationship("User", backref=db.backref("student", uselist=False), lazy=True)
    
    def __repr__(self):
        return f'<Student {self.student_id}>'
    
    # Indexes
    __table_args__ = (
        db.Index("idx_students_student_id", 'student_id', unique=True),
        db.Index("idx_students_name", 'name'),
        db.Index("idx_students_contact", 'contact'),
        db.Index("idx_students_year_cgpa", 'graduation_year', 'cgpa'),
    )
