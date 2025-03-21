from datetime import datetime
from models import AuditLog  # Import the AuditLog model
from database import db  # Import the SQLAlchemy instance

def log_action(user_id, action):
    """
    Log a user action in the database.
    :param user_id: ID of the user performing the action.
    :param action: Description of the action (e.g., "Login", "Add Password").
    """
    audit_log = AuditLog(user_id=user_id, action=action, timestamp=datetime.utcnow())
    db.session.add(audit_log)
    db.session.commit()