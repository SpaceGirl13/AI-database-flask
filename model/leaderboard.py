""" Database model for Submodule 3 Leaderboard """
from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class LeaderboardEntry(db.Model):
    """
    LeaderboardEntry Model

    Represents a score entry in the submodule 3 game leaderboard.

    Attributes:
        id (Column): Primary key, unique identifier for the entry.
        _uid (Column): The user's unique identifier.
        _player_name (Column): The player's display name.
        _score (Column): The score achieved.
        _correct_answers (Column): Number of correct answers.
        _timestamp (Column): When the score was recorded.
    """
    __tablename__ = 'leaderboard'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.String(255), nullable=False)
    _player_name = db.Column(db.String(255), nullable=False)
    _score = db.Column(db.Integer, nullable=False)
    _correct_answers = db.Column(db.Integer, nullable=False)
    _timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, uid, player_name, score, correct_answers, timestamp=None):
        self._uid = uid
        self._player_name = player_name
        self._score = score
        self._correct_answers = correct_answers
        self._timestamp = timestamp if timestamp else datetime.utcnow()

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def player_name(self):
        return self._player_name

    @player_name.setter
    def player_name(self, value):
        self._player_name = value

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
            "uid": self._uid,
            "playerName": self._player_name,
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


"""Database Initialization"""
import random


def initLeaderboard():
    """Initialize leaderboard with sample data"""
    with app.app_context():
        db.create_all()

        # Check if leaderboard already has entries
        if LeaderboardEntry.query.count() > 0:
            print("Leaderboard already initialized")
            return

        # Sample player names
        players = [
            ("alice", "Alice Johnson"),
            ("bob", "Bob Smith"),
            ("charlie", "Charlie Brown"),
            ("diana", "Diana Prince"),
            ("evan", "Evan Williams"),
            ("fiona", "Fiona Apple"),
            ("george", "George Lucas"),
            ("hannah", "Hannah Montana"),
            ("ivan", "Ivan Petrov"),
            ("julia", "Julia Roberts"),
        ]

        # Create 10 sample leaderboard entries
        for i, (uid, name) in enumerate(players):
            score = random.randint(60, 100)
            correct = score // 10
            entry = LeaderboardEntry(
                uid=uid,
                player_name=name,
                score=score,
                correct_answers=correct
            )
            db.session.add(entry)

        db.session.commit()
        print(f"Initialized {LeaderboardEntry.query.count()} leaderboard entries")
