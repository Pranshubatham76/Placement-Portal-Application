from app import db
from app.models.user import User


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    #password = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Admin {self.name}>'

    # Relationship
    user = db.relationship("User", backref=db.backref("admin", uselist=False), lazy=True)