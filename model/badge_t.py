"""Database models for Badge System"""
from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class Badge(db.Model):
    """
    Badge Model
    
    Represents a badge definition with metadata.
    
    Attributes:
        id (Column): Primary key, unique identifier for the badge.
        _badge_id (Column): Unique string identifier (e.g., 'delightful_data_scientist').
        _name (Column): Display name of the badge.
        _description (Column): Description of what the badge represents.
        _requirement (Column): What is required to earn this badge.
        _image_url (Column): URL to the badge image.
    """
    __tablename__ = 'badges'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    _badge_id = db.Column(db.String(255), unique=True, nullable=False)
    _name = db.Column(db.String(255), nullable=False)
    _description = db.Column(db.Text, nullable=False)
    _requirement = db.Column(db.String(255), nullable=False)
    _image_url = db.Column(db.Text, nullable=False)

    # Many-to-many relationship with User
    # Avoid forcing a subquery load on User (which can fail if the table is missing). Use 'select' to load lazily when accessed.
    # Add 'overlaps' to the backref to silence SAWarnings about overlapping relationships
    users = db.relationship('User', secondary='user_badges', backref=db.backref('badge_list', lazy='select', overlaps='user_badges_rel,users'))

    def __init__(self, badge_id, name, description, requirement, image_url):
        self._badge_id = badge_id
        self._name = name
        self._description = description
        self._requirement = requirement
        self._image_url = image_url

    @property
    def badge_id(self):
        return self._badge_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def requirement(self):
        return self._requirement

    @property
    def image_url(self):
        return self._image_url

    def read(self):
        return {
            "id": self._badge_id,
            "name": self._name,
            "description": self._description,
            "requirement": self._requirement,
            "image_url": self._image_url
        }

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception:
            # Rollback on any DB error (IntegrityError, OperationalError, etc.)
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return None
        except Exception:
            db.session.rollback()
            return None


class UserBadge(db.Model):
    """
    UserBadge Model
    
    A many-to-many relationship between users and badges.
    Tracks when a user earned a badge.
    
    Attributes:
        user_id (Column): Foreign key referencing the users table.
        badge_id (Column): Foreign key referencing the badges table.
        awarded_at (Column): Timestamp when the badge was awarded.
    """
    __tablename__ = 'user_badges'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # Add ON DELETE CASCADE so rows are removed if the parent user or badge is deleted
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id', ondelete='CASCADE'), primary_key=True)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Add 'overlaps' to avoid SAWarning about relationship overlap with 'Badge.users' and 'User.badge_list'
    user = db.relationship('User', backref=db.backref('user_badges_rel', cascade='all, delete-orphan', overlaps='badge_list,users'), overlaps='badge_list,users')
    badge = db.relationship('Badge', backref=db.backref('user_badges_rel', cascade='all, delete-orphan', overlaps='badge_list,users'), overlaps='badge_list,users')

    def __init__(self, user_id, badge_id):
        self.user_id = user_id
        self.badge_id = badge_id

    def read(self):
        return {
            "user_id": self.user_id,
            "badge_id": self.badge_id,
            "awarded_at": self.awarded_at.isoformat() if self.awarded_at else None
        }

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception:
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return None
        except Exception:
            db.session.rollback()
            return None


def init_badges():
    """Initialize the badge database with badge definitions"""
    with app.app_context():
        db.create_all()
        
        badge_definitions = {
            'delightful_data_scientist': {
                'name': 'Delightful Data Scientist',
                'description': 'Mastered Math and CS prompt engineering',
                'requirement': 'Complete CS and Math on Submodule 2',
                'image_url': 'https://github.com/user-attachments/assets/d3d6f596-cae3-401d-9390-a3721aa7cfb3'
            },
            'perfect_prompt_engineer': {
                'name': 'Perfect Prompt Engineer',
                'description': 'Demonstrated expertise in crafting effective AI prompts',
                'requirement': 'Complete Submodule 2',
                'image_url': 'https://github.com/user-attachments/assets/65a9a19a-4f0a-4e08-8a70-cd37c1e75b7d'
            },
            'prodigy_problem_solver': {
                'name': 'Prodigy Problem Solver',
                'description': 'Applied AI knowledge to solve real-world challenges',
                'requirement': 'Complete Submodule 3',
                'image_url': 'https://github.com/user-attachments/assets/d85f749c-2380-4427-96af-20b462e65514'
            },
            'responsible_ai_master': {
                'name': 'Responsible AI Master',
                'description': 'Achieved comprehensive understanding of ethical AI practices',
                'requirement': 'Complete Entire Quest',
                'image_url': 'https://github.com/user-attachments/assets/93e2fc3f-4ab4-4eef-8369-6a4c3a18f660'
            },
            'super_smart_genius': {
                'name': 'Super Smart Genius',
                'description': 'Ranked among top performers in the platform',
                'requirement': 'Make the Leaderboard',
                'image_url': 'https://github.com/user-attachments/assets/6a96f46c-b926-4c44-8926-1ffbba007a05'
            },
            'intelligent_instructor': {
                'name': 'Intelligent Instructor',
                'description': 'Crafted a high-quality, effective AI prompt',
                'requirement': 'Create a "Good" Prompt',
                'image_url': 'https://github.com/user-attachments/assets/b1a7fc47-da59-4f14-a8d0-2b4c36df7cc5'
            },
            'sensational_surveyor': {
                'name': 'Sensational Surveyor',
                'description': 'Provided valuable feedback to improve the platform',
                'requirement': 'Submit the Survey',
                'image_url': 'https://github.com/user-attachments/assets/5aebe49f-d1e5-4340-bba0-7e3e5b3afae2'
            }
        }
        
        # Create badges if they don't exist
        for badge_key, badge_data in badge_definitions.items():
            existing_badge = Badge.query.filter_by(_badge_id=badge_key).first()
            if not existing_badge:
                badge = Badge(
                    badge_id=badge_key,
                    name=badge_data['name'],
                    description=badge_data['description'],
                    requirement=badge_data['requirement'],
                    image_url=badge_data['image_url']
                )
                badge.create()
        
        print(f"Initialized {Badge.query.count()} badges")