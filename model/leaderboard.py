""" Database model for Submodule 3 Leaderboard - Normalized Transaction Data """
from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class LeaderboardEntry(db.Model):
    """
    LeaderboardEntry Model - Normalized Transaction Data

    Represents a single score transaction in the submodule 3 game leaderboard.
    Uses proper foreign key relationship to User table for normalization.
    Each entry is a transaction recording a game attempt.

    Attributes:
        id (Column): Primary key, unique identifier for the entry.
        user_id (Column): Foreign key to users table (required for score tracking).
        _score (Column): The score achieved in this game transaction.
        _correct_answers (Column): Number of correct answers in this attempt.
        _timestamp (Column): When the score transaction was recorded.
    """
    __tablename__ = 'leaderboard'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _score = db.Column(db.Integer, nullable=False)
    _correct_answers = db.Column(db.Integer, nullable=False)
    _timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, score, correct_answers, timestamp=None):
        self.user_id = user_id
        self._score = score
        self._correct_answers = correct_answers
        self._timestamp = timestamp if timestamp else datetime.utcnow()

    def _get_user(self):
        """Helper to get the related User object"""
        from model.user import User
        return User.query.get(self.user_id)

    @property
    def uid(self):
        """Get uid from related User object (normalized access)"""
        user = self._get_user()
        if user:
            return user.uid
        return None

    @property
    def player_name(self):
        """Get player name from related User object (normalized access)"""
        user = self._get_user()
        if user:
            return user.name
        return "Unknown"

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def correct_answers(self):
        return self._correct_answers

    @correct_answers.setter
    def correct_answers(self, value):
        self._correct_answers = value

    @property
    def timestamp(self):
        return self._timestamp

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
            "uid": self.uid,  # Derived from User relationship
            "playerName": self.player_name,  # Derived from User relationship
            "score": self._score,
            "correctAnswers": self._correct_answers,
            "timestamp": self._timestamp.isoformat() if self._timestamp else None
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    @staticmethod
    def get_top_scores(limit=10):
        """Get top scores sorted by score (desc) then timestamp (asc)"""
        return LeaderboardEntry.query.order_by(
            LeaderboardEntry._score.desc(),
            LeaderboardEntry._timestamp.asc()
        ).limit(limit).all()

    @staticmethod
    def get_all_scores():
        """Get all scores sorted by score (desc) then timestamp (asc)"""
        return LeaderboardEntry.query.order_by(
            LeaderboardEntry._score.desc(),
            LeaderboardEntry._timestamp.asc()
        ).all()

    @staticmethod
    def get_user_scores(user_id):
        """Get all score transactions for a specific user"""
        return LeaderboardEntry.query.filter_by(user_id=user_id).order_by(
            LeaderboardEntry._timestamp.desc()
        ).all()

    @staticmethod
    def get_user_best_score(user_id):
        """Get user's best score transaction"""
        return LeaderboardEntry.query.filter_by(user_id=user_id).order_by(
            LeaderboardEntry._score.desc()
        ).first()


"""Database Initialization"""
import random


def initLeaderboard():
    """Initialize leaderboard with sample transaction data"""
    from model.user import User

    with app.app_context():
        db.create_all()

        # Check if leaderboard already has entries
        if LeaderboardEntry.query.count() > 0:
            print("Leaderboard already initialized")
            return

        # Get existing users to link leaderboard entries (normalized relationship)
        users = User.query.all()

        if not users:
            print("No users found. Please initialize users first.")
            return

        # Create sample leaderboard transaction entries for existing users
        # Each user gets 1-3 game attempts (transactions)
        for user in users:
            num_attempts = random.randint(1, 3)
            for _ in range(num_attempts):
                score = random.randint(60, 100)
                correct = score // 10
                entry = LeaderboardEntry(
                    user_id=user.id,
                    score=score,
                    correct_answers=correct
                )
                db.session.add(entry)

        db.session.commit()
        print(f"Initialized {LeaderboardEntry.query.count()} leaderboard transaction entries")
