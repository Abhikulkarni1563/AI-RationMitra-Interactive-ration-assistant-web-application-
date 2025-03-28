# add_feedback.py

from main import app
from extensions import db
from models import Feedback
from datetime import datetime

with app.app_context():
    feedback1 = Feedback(
        username="Aarav Mehta",
        message="Ration Mitraa is really helpful in rural areas.",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rating=5
    )

    feedback2 = Feedback(
        username="Priya Sharma",
        message="The interface is clean and easy to use. Great job!",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rating=4
    )

    feedback3 = Feedback(
        username="Ravi Kumar",
        message="Could improve speed during peak hours.",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rating=3
    )

    db.session.add_all([feedback1, feedback2, feedback3])
    db.session.commit()

    print("✅ Sample feedbacks added!")
