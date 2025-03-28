# reset_feedback.py

from main import app
from extensions import db
from models import Feedback

with app.app_context():
    # Optional: Drop the Feedback table (uncomment to use)
    Feedback.__table__.drop(db.engine, checkfirst=True)

    # Recreate all tables (includes Feedback)
    db.create_all()

    # Confirm the columns in Feedback table
    print("✅ Feedback table columns:")
    for column in Feedback.__table__.columns:
        print(f"  - {column.name} ({column.type})")
