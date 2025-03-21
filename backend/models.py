from datetime import datetime
from database import db  # Import the SQLAlchemy instance from database.py

class AuditLog(db.Model):
    """
    Model to store audit logs of user actions.
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each log entry
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Links to the user
    action = db.Column(db.String(200), nullable=False)  # Description of the action (e.g., "Login", "Add Password")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp of the action