""" Database models for Survey Results (Submodule 1) """
from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class SurveyUser(db.Model):
    """
    SurveyUser Model

    Represents users who have taken the AI survey.

    Attributes:
        id (Column): Primary key, unique identifier for the user.
        _username (Column): The user's username.
        _email (Column): The user's email address.
    """
    __tablename__ = 'survey_users'

    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column(db.String(255), unique=True, nullable=False)
    _email = db.Column(db.String(255), unique=False, nullable=True)

    # One-to-many relationship with SurveyResponse
    responses = db.relationship('SurveyResponse', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email=None):
        self._username = username
        self._email = email

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

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
            "email": self._email
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


class SurveyResponse(db.Model):
    """
    SurveyResponse Model

    Represents a survey response from a user.

    Attributes:
        id (Column): Primary key, unique identifier for the response.
        user_id (Column): Foreign key referencing the survey_users table.
        _uses_ai_schoolwork (Column): Whether the user uses AI for schoolwork (Yes/No).
        _policy_perspective (Column): User's perspective on AI policy (FRQ text).
        _completed_at (Column): Timestamp when the survey was completed.
        _badge_awarded (Column): Whether a badge was awarded for this response.
    """
    __tablename__ = 'survey_responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('survey_users.id'), nullable=False)
    _uses_ai_schoolwork = db.Column(db.String(10), nullable=False)
    _policy_perspective = db.Column(db.Text, nullable=True)
    _completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    _badge_awarded = db.Column(db.Boolean, default=False)

    # One-to-many relationship with AIToolPreference
    preferences = db.relationship('AIToolPreference', backref='response', lazy=True, cascade='all, delete-orphan')

    def __init__(self, user_id, uses_ai_schoolwork, policy_perspective=None, badge_awarded=False):
        self.user_id = user_id
        self._uses_ai_schoolwork = uses_ai_schoolwork
        self._policy_perspective = policy_perspective
        self._badge_awarded = badge_awarded

    @property
    def uses_ai_schoolwork(self):
        return self._uses_ai_schoolwork

    @uses_ai_schoolwork.setter
    def uses_ai_schoolwork(self, value):
        self._uses_ai_schoolwork = value

    @property
    def policy_perspective(self):
        return self._policy_perspective

    @policy_perspective.setter
    def policy_perspective(self, value):
        self._policy_perspective = value

    @property
    def completed_at(self):
        return self._completed_at

    @property
    def badge_awarded(self):
        return self._badge_awarded

    @badge_awarded.setter
    def badge_awarded(self, value):
        self._badge_awarded = value

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
            "uses_ai_schoolwork": self._uses_ai_schoolwork,
            "policy_perspective": self._policy_perspective,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            "badge_awarded": self._badge_awarded,
            "preferences": [pref.read() for pref in self.preferences]
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


class AIToolPreference(db.Model):
    """
    AIToolPreference Model

    Represents a user's preferred AI tool for a specific subject.

    Attributes:
        id (Column): Primary key, unique identifier for the preference.
        response_id (Column): Foreign key referencing the survey_responses table.
        _subject (Column): The subject (english, math, science, cs, history).
        _ai_tool (Column): The preferred AI tool (ChatGPT, Claude, Gemini, Copilot).
    """
    __tablename__ = 'ai_tool_preferences'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    _subject = db.Column(db.String(50), nullable=False)
    _ai_tool = db.Column(db.String(50), nullable=False)

    def __init__(self, response_id, subject, ai_tool):
        self.response_id = response_id
        self._subject = subject
        self._ai_tool = ai_tool

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def ai_tool(self):
        return self._ai_tool

    @ai_tool.setter
    def ai_tool(self, value):
        self._ai_tool = value

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
            "response_id": self.response_id,
            "subject": self._subject,
            "ai_tool": self._ai_tool
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


"""Database Creation and Testing"""


def initSurveyResults():
    """Initialize survey results with staged test data"""
    with app.app_context():
        db.create_all()

        # Staged test users
        users_data = [
            {"username": "alice_student", "email": "alice@example.com"},
            {"username": "bob_learner", "email": "bob@example.com"},
            {"username": "charlie_coder", "email": "charlie@example.com"},
            {"username": "diana_dev", "email": "diana@example.com"},
            {"username": "evan_engineer", "email": "evan@example.com"},
            {"username": "fiona_future", "email": "fiona@example.com"},
            {"username": "george_geek", "email": "george@example.com"},
            {"username": "hannah_hacker", "email": "hannah@example.com"},
            {"username": "ivan_innovator", "email": "ivan@example.com"},
        ]

        # Staged survey responses with tool preferences
        responses_data = [
            {
                "username": "alice_student",
                "uses_ai": "Yes",
                "policy_perspective": "I believe AI policies need to strike a balance between preventing academic dishonesty and allowing students to learn how to use AI as a tool. Rather than banning AI completely, I think we should learn how to use it ethically and responsibly.",
                "badge_awarded": True,
                "preferences": {
                    "english": "ChatGPT",
                    "math": "Claude",
                    "science": "ChatGPT",
                    "cs": "Claude",
                    "history": "Gemini"
                }
            },
            {
                "username": "bob_learner",
                "uses_ai": "Yes",
                "policy_perspective": "I believe AI policies should focus on helping students learn responsibly. AI should support understanding, brainstorming, and feedback without replacing original thinking or academic honesty.",
                "badge_awarded": True,
                "preferences": {
                    "english": "ChatGPT",
                    "math": "Claude",
                    "science": "Claude",
                    "cs": "Gemini",
                    "history": "Gemini"
                }
            },
            {
                "username": "charlie_coder",
                "uses_ai": "Yes",
                "policy_perspective": "AI should be allowed sometimes in classes as a way for students to enhance their learning.",
                "badge_awarded": True,
                "preferences": {
                    "english": "Claude",
                    "math": "ChatGPT",
                    "science": "Gemini",
                    "cs": "Claude",
                    "history": "ChatGPT"
                }
            },
            {
                "username": "diana_dev",
                "uses_ai": "Yes",
                "policy_perspective": "I would want to use AI to provide examples and simplify concepts that I don't understand.",
                "badge_awarded": True,
                "preferences": {
                    "english": "ChatGPT",
                    "math": "Claude",
                    "science": "Claude",
                    "cs": "Gemini",
                    "history": "Gemini"
                }
            },
            {
                "username": "evan_engineer",
                "uses_ai": "Yes",
                "policy_perspective": "I want to use AI effectively to learn by using examples and practice problems.",
                "badge_awarded": True,
                "preferences": {
                    "english": "ChatGPT",
                    "math": "Gemini",
                    "science": "ChatGPT",
                    "cs": "Gemini",
                    "history": "Gemini"
                }
            },
            {
                "username": "fiona_future",
                "uses_ai": "Yes",
                "policy_perspective": "AI should be allowed to use in classes. AI can act as a tutor to help students learn information rather than doing their homework for them.",
                "badge_awarded": True,
                "preferences": {
                    "english": "Claude",
                    "math": "Claude",
                    "science": "Gemini",
                    "cs": "Claude",
                    "history": "Copilot"
                }
            },
            {
                "username": "george_geek",
                "uses_ai": "Yes",
                "policy_perspective": "AI tools should be embraced in education as they represent the future of work. Learning to use them effectively is a valuable skill.",
                "badge_awarded": True,
                "preferences": {
                    "english": "ChatGPT",
                    "math": "Copilot",
                    "science": "ChatGPT",
                    "cs": "Copilot",
                    "history": "Copilot"
                }
            },
            {
                "username": "hannah_hacker",
                "uses_ai": "Yes",
                "policy_perspective": "I think it's important to cite when I've used AI and be transparent about how I've incorporated it into my work.",
                "badge_awarded": True,
                "preferences": {
                    "english": "Gemini",
                    "math": "Claude",
                    "science": "Claude",
                    "cs": "Gemini",
                    "history": "Gemini"
                }
            },
            {
                "username": "ivan_innovator",
                "uses_ai": "Yes",
                "policy_perspective": "AI should enhance my learning, not replace it. I would still write my own original responses and do my own critical thinking.",
                "badge_awarded": True,
                "preferences": {
                    "english": "Gemini",
                    "math": "ChatGPT",
                    "science": "Gemini",
                    "cs": "Claude",
                    "history": "ChatGPT"
                }
            },
        ]

        # Create users
        users = {}
        for user_data in users_data:
            user = SurveyUser(username=user_data["username"], email=user_data["email"])
            try:
                user.create()
                users[user_data["username"]] = user
            except IntegrityError:
                db.session.rollback()
                print(f"User already exists: {user_data['username']}")
                existing_user = SurveyUser.query.filter_by(_username=user_data["username"]).first()
                if existing_user:
                    users[user_data["username"]] = existing_user

        # Create responses and preferences
        for response_data in responses_data:
            user = users.get(response_data["username"])
            if user:
                response = SurveyResponse(
                    user_id=user.id,
                    uses_ai_schoolwork=response_data["uses_ai"],
                    policy_perspective=response_data["policy_perspective"],
                    badge_awarded=response_data["badge_awarded"]
                )
                try:
                    response.create()

                    # Create AI tool preferences for each subject
                    for subject, ai_tool in response_data["preferences"].items():
                        preference = AIToolPreference(
                            response_id=response.id,
                            subject=subject,
                            ai_tool=ai_tool
                        )
                        preference.create()

                except IntegrityError:
                    db.session.rollback()
                    print(f"Response already exists for user: {response_data['username']}")
