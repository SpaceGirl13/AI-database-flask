from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(64), default="Other")
    github_username = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    github_issue_url = db.Column(db.String(512), nullable=True)


    def __init__(self, title, body, type="Other", github_username=None):
        self.title = title
        self.body = body
        self.type = type
        self.github_username = github_username


    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "type": self.type,
            "github_username": self.github_username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "github_issue_url": self.github_issue_url
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


def initFeedback():
    """Initialize feedback with sample data"""
    with app.app_context():
        db.create_all()

        # Check if feedback already has entries
        if Feedback.query.count() > 0:
            print("Feedback already initialized")
            return

        # Sample feedback entries
        sample_feedback = [
            {
                "title": "Great learning platform!",
                "body": "I really enjoyed using AI Study Buddy. The prompts and challenges helped me understand AI concepts better.",
                "type": "General",
                "github_username": "student_001"
            },
            {
                "title": "Feature request: Dark mode",
                "body": "It would be great to have a dark mode option for studying at night.",
                "type": "Feature Request",
                "github_username": "student_002"
            },
            {
                "title": "Bug: Survey not loading",
                "body": "Sometimes the survey page takes a long time to load. Could you optimize it?",
                "type": "Bug Report",
                "github_username": "student_003"
            },
            {
                "title": "Love the badge system",
                "body": "The badges motivate me to complete all the submodules. Great gamification!",
                "type": "General",
                "github_username": "student_004"
            },
            {
                "title": "Suggestion for more subjects",
                "body": "Could you add more subjects like economics or social studies to the question bank?",
                "type": "Feature Request",
                "github_username": "student_005"
            }
        ]

        for fb_data in sample_feedback:
            feedback = Feedback(
                title=fb_data["title"],
                body=fb_data["body"],
                type=fb_data["type"],
                github_username=fb_data["github_username"]
            )
            db.session.add(feedback)

        db.session.commit()
        print(f"Initialized {Feedback.query.count()} feedback entries")
