from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class Feedback(db.Model):
    """
    Feedback Model - Normalized Transaction Data

    Represents a single feedback transaction/submission from a user.
    Uses proper foreign key relationship to User table for normalization.

    Attributes:
        id (Column): Primary key, unique identifier for the feedback entry.
        user_id (Column): Foreign key to users table (nullable for anonymous feedback).
        title (Column): The feedback title/subject.
        body (Column): The detailed feedback content.
        type (Column): Category of feedback (Bug, Feature Request, Inquiry, Other).
        created_at (Column): Timestamp when feedback was submitted.
        github_issue_url (Column): URL of the created GitHub issue (if any).
    """
    __tablename__ = 'feedbacks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(64), default="Other")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    github_issue_url = db.Column(db.String(512), nullable=True)

    def __init__(self, title, body, type="Other", user_id=None):
        self.title = title
        self.body = body
        self.type = type
        self.user_id = user_id

    @property
    def username(self):
        """Get username from related User object (normalized access)"""
        from model.user import User
        if self.user_id:
            user = User.query.get(self.user_id)
            if user:
                return user.uid
        return "Anonymous"

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
            "user_id": self.user_id,
            "username": self.username,  # Derived from User relationship
            "title": self.title,
            "body": self.body,
            "type": self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "github_issue_url": self.github_issue_url
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


def initFeedback():
    """Initialize feedback with sample transaction data"""
    from model.user import User

    with app.app_context():
        db.create_all()

        # Check if feedback already has entries
        if Feedback.query.count() > 0:
            print("Feedback already initialized")
            return

        # Get existing users to link feedback (normalized relationship)
        users = User.query.limit(5).all()

        # Sample feedback transaction entries
        sample_feedback = [
            {
                "title": "Great learning platform!",
                "body": "I really enjoyed using AI Study Buddy. The prompts and challenges helped me understand AI concepts better.",
                "type": "General",
            },
            {
                "title": "Feature request: Dark mode",
                "body": "It would be great to have a dark mode option for studying at night.",
                "type": "Feature Request",
            },
            {
                "title": "Bug: Survey not loading",
                "body": "Sometimes the survey page takes a long time to load. Could you optimize it?",
                "type": "Bug",
            },
            {
                "title": "Love the badge system",
                "body": "The badges motivate me to complete all the submodules. Great gamification!",
                "type": "General",
            },
            {
                "title": "Suggestion for more subjects",
                "body": "Could you add more subjects like economics or social studies to the question bank?",
                "type": "Feature Request",
            }
        ]

        for i, fb_data in enumerate(sample_feedback):
            # Link to existing user if available (normalized foreign key)
            user_id = users[i].id if i < len(users) else None

            feedback = Feedback(
                title=fb_data["title"],
                body=fb_data["body"],
                type=fb_data["type"],
                user_id=user_id
            )
            db.session.add(feedback)

        db.session.commit()
        print(f"Initialized {Feedback.query.count()} feedback transaction entries")
