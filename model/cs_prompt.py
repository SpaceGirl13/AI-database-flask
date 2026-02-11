from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class CSPrompt(db.Model):
    """
    CS Prompt Model - Normalized Transaction Data

    Represents a single CS prompt submission from a user for Activity 3.
    Uses proper foreign key relationship to User table for normalization.

    Attributes:
        id (Column): Primary key, unique identifier for the prompt entry.
        user_id (Column): Foreign key to users table (nullable for anonymous).
        prompt (Column): The prompt text submitted by the user.
        prompt_type (Column): Type of prompt (Good, Bad, Custom).
        score (Column): Analysis score if analyzed (0-100).
        improved_version (Column): AI-improved version of the prompt.
        created_at (Column): Timestamp when prompt was submitted.
    """
    __tablename__ = 'cs_prompts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    prompt = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(32), default="Custom")
    score = db.Column(db.Integer, nullable=True)
    improved_version = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, prompt, prompt_type="Custom", user_id=None, score=None, improved_version=None):
        self.prompt = prompt
        self.prompt_type = prompt_type
        self.user_id = user_id
        self.score = score
        self.improved_version = improved_version

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
            "username": self.username,
            "prompt": self.prompt,
            "type": self.prompt_type,
            "score": self.score,
            "improved_version": self.improved_version,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def update(self, data):
        """Update prompt with new data"""
        if 'prompt' in data:
            self.prompt = data['prompt']
        if 'prompt_type' in data:
            self.prompt_type = data['prompt_type']
        if 'score' in data:
            self.score = data['score']
        if 'improved_version' in data:
            self.improved_version = data['improved_version']

        try:
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    @staticmethod
    def get_all():
        """Get all CS prompts"""
        return CSPrompt.query.order_by(CSPrompt.created_at.desc()).all()

    @staticmethod
    def get_by_type(prompt_type, limit=10):
        """Get prompts filtered by type"""
        return CSPrompt.query.filter_by(prompt_type=prompt_type).order_by(
            CSPrompt.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_recent(limit=10):
        """Get recent prompts"""
        return CSPrompt.query.order_by(CSPrompt.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_by_user(user_id, limit=10):
        """Get prompts by user"""
        return CSPrompt.query.filter_by(user_id=user_id).order_by(
            CSPrompt.created_at.desc()
        ).limit(limit).all()


def initCSPrompts():
    """Initialize CS prompts with sample transaction data"""
    from model.user import User

    with app.app_context():
        db.create_all()

        # Check if CS prompts already has entries
        if CSPrompt.query.count() > 0:
            print("CS Prompts already initialized")
            return

        # Sample CS prompt transaction entries
        sample_prompts = [
            {
                "prompt": "Write a Python function that calculates the factorial of a number using recursion. Include docstring and examples.",
                "prompt_type": "Good",
                "score": 100
            },
            {
                "prompt": "Create a JavaScript function to validate email addresses using regex. Explain the pattern used.",
                "prompt_type": "Good",
                "score": 95
            },
            {
                "prompt": "Debug this Python code that has an IndexError. Explain step-by-step how to fix it.",
                "prompt_type": "Good",
                "score": 90
            },
            {
                "prompt": "Write a simple sorting algorithm in Python with comments explaining each step. I'm a beginner.",
                "prompt_type": "Good",
                "score": 85
            },
            {
                "prompt": "Implement a binary search function in Python. Include time complexity analysis and edge case handling.",
                "prompt_type": "Good",
                "score": 95
            },
            {
                "prompt": "make code",
                "prompt_type": "Bad",
                "score": 10
            },
            {
                "prompt": "fix my error",
                "prompt_type": "Bad",
                "score": 15
            },
            {
                "prompt": "write function",
                "prompt_type": "Bad",
                "score": 20
            }
        ]

        # Get existing users to link prompts (normalized relationship)
        users = User.query.limit(5).all()

        for i, prompt_data in enumerate(sample_prompts):
            # Link to existing user if available (normalized foreign key)
            user_id = users[i % len(users)].id if users else None

            cs_prompt = CSPrompt(
                prompt=prompt_data["prompt"],
                prompt_type=prompt_data["prompt_type"],
                score=prompt_data.get("score"),
                user_id=user_id
            )
            db.session.add(cs_prompt)

        db.session.commit()
        print(f"Initialized {CSPrompt.query.count()} CS prompt transaction entries")
