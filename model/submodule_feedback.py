""" Database model for Submodule Feedback Survey """
from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class SubmoduleFeedback(db.Model):
    """
    SubmoduleFeedback Model

    Represents feedback from users for submodules 2 and 3.

    Attributes:
        id (Column): Primary key, unique identifier for the feedback.
        _username (Column): The user's username.
        _rating (Column): Rating given (1-5 scale).
        _category (Column): Which submodule (submodule2, submodule3).
        _comments (Column): Additional comments from the user.
        _timestamp (Column): When the feedback was submitted.
    """
    __tablename__ = 'submodule_feedback'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column(db.String(255), nullable=False)
    _rating = db.Column(db.Integer, nullable=False)
    _category = db.Column(db.String(50), nullable=False)
    _comments = db.Column(db.Text, nullable=True)
    _timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, rating, category, comments=None, timestamp=None):
        self._username = username
        self._rating = rating
        self._category = category
        self._comments = comments
        self._timestamp = timestamp if timestamp else datetime.utcnow()

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def comments(self):
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

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
            "username": self._username,
            "rating": self._rating,
            "category": self._category,
            "comments": self._comments,
            "timestamp": self._timestamp.isoformat() if self._timestamp else None
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    @staticmethod
    def get_by_category(category):
        """Get all feedback for a specific category (submodule2, submodule3)"""
        return SubmoduleFeedback.query.filter_by(_category=category).order_by(
            SubmoduleFeedback._timestamp.desc()
        ).all()

    @staticmethod
    def get_all_feedback():
        """Get all feedback sorted by timestamp (newest first)"""
        return SubmoduleFeedback.query.order_by(
            SubmoduleFeedback._timestamp.desc()
        ).all()

    @staticmethod
    def get_average_rating(category=None):
        """Get average rating, optionally filtered by category"""
        from sqlalchemy import func
        query = db.session.query(func.avg(SubmoduleFeedback._rating))
        if category:
            query = query.filter(SubmoduleFeedback._category == category)
        result = query.scalar()
        return round(result, 2) if result else 0


"""Database Initialization"""
import random


def initSubmoduleFeedback():
    """Initialize feedback with sample data"""
    with app.app_context():
        db.create_all()

        # Check if feedback already has entries
        if SubmoduleFeedback.query.count() > 0:
            print("Submodule feedback already initialized")
            return

        # Sample usernames
        usernames = [f"student_{i:03d}" for i in range(1, 21)]

        # Sample comments
        sample_comments = [
            "Great learning experience!",
            "Very helpful for understanding AI concepts.",
            "Could use more examples.",
            "The prompts were interesting and challenging.",
            "I learned a lot about how to interact with AI.",
            "Would recommend to other students.",
            "Some questions were too difficult.",
            "Really enjoyed the interactive elements.",
            "Helped me understand prompt engineering better.",
            "Good balance of theory and practice.",
            None,  # Some entries without comments
            None,
        ]

        categories = ['submodule2', 'submodule3']

        # Create 20 sample feedback entries
        for username in usernames:
            category = random.choice(categories)
            rating = random.randint(3, 5)  # Ratings between 3-5
            comments = random.choice(sample_comments)

            feedback = SubmoduleFeedback(
                username=username,
                rating=rating,
                category=category,
                comments=comments
            )
            db.session.add(feedback)

        db.session.commit()
        print(f"Initialized {SubmoduleFeedback.query.count()} submodule feedback entries")
