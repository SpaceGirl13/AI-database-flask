""" Database models for Survey Results (Submodule 1) """
from __init__ import app, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class SurveyResponse(db.Model):
    """
    SurveyResponse Model

    Represents a survey response from a user.

    Attributes:
        id (Column): Primary key, unique identifier for the response.
        user_id (Column): User identifier (sequential).
        _username (Column): The user's username.
        _uses_ai_schoolwork (Column): Whether the user uses AI for schoolwork (Yes/No).
        _policy_perspective (Column): User's perspective on AI policy (FRQ text).
        _completed_at (Column): Timestamp when the survey was completed.
        _badge_awarded (Column): Whether a badge was awarded for this response.
    """
    __tablename__ = 'survey_responses'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    _username = db.Column(db.String(255), nullable=False)
    _uses_ai_schoolwork = db.Column(db.String(10), nullable=False)
    _policy_perspective = db.Column(db.Text, nullable=True)
    _completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    _badge_awarded = db.Column(db.Boolean, default=False)

    # One-to-many relationship with AIToolPreference
    preferences = db.relationship('AIToolPreference', backref='response', lazy=True, cascade='all, delete-orphan')

    def __init__(self, user_id, username, uses_ai_schoolwork, policy_perspective=None, badge_awarded=False):
        self.user_id = user_id
        self._username = username
        self._uses_ai_schoolwork = uses_ai_schoolwork
        self._policy_perspective = policy_perspective
        self._badge_awarded = badge_awarded

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

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
            "username": self._username,
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
    __table_args__ = {'extend_existing': True}

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
import random


def initSurveyResults():
    """Initialize survey results with 100 staged test responses"""
    with app.app_context():
        db.create_all()

        # AI tools and their weighted probabilities for each subject
        ai_tools = ['ChatGPT', 'Claude', 'Gemini', 'Copilot']

        # Subject-specific weights (some tools are more popular for certain subjects)
        subject_weights = {
            'english': [0.35, 0.25, 0.25, 0.15],  # ChatGPT popular for writing
            'math': [0.20, 0.35, 0.25, 0.20],     # Claude good for math
            'science': [0.30, 0.25, 0.30, 0.15],  # ChatGPT/Gemini for science
            'cs': [0.25, 0.30, 0.20, 0.25],       # Claude/Copilot for coding
            'history': [0.30, 0.20, 0.35, 0.15],  # Gemini for research
        }

        # Sample FRQ responses
        frq_responses = [
            "I believe AI policies need to strike a balance between preventing academic dishonesty and allowing students to learn how to use AI as a tool. Rather than banning AI completely, I think we should learn how to use it ethically and responsibly.",
            "I believe AI policies should focus on helping students learn responsibly. AI should support understanding, brainstorming, and feedback without replacing original thinking or academic honesty.",
            "AI should be allowed sometimes in classes as a way for students to enhance their learning.",
            "I would want to use AI to provide examples and simplify concepts that I don't understand.",
            "I want to use AI effectively to learn by using examples and practice problems.",
            "AI should be allowed to use in classes. AI can act as a tutor to help students learn information rather than doing their homework for them.",
            "AI tools should be embraced in education as they represent the future of work. Learning to use them effectively is a valuable skill.",
            "I think it's important to cite when I've used AI and be transparent about how I've incorporated it into my work.",
            "AI should enhance my learning, not replace it. I would still write my own original responses and do my own critical thinking.",
            "Schools should teach students how to use AI responsibly rather than banning it outright. AI literacy is becoming essential.",
            "I use AI to check my work and get feedback, but I always do the initial thinking myself.",
            "AI helps me understand difficult concepts by explaining them in different ways until I get it.",
            "I think AI should be allowed for research and brainstorming, but not for writing final answers.",
            "Using AI as a study buddy has helped me learn more efficiently and retain information better.",
            "AI policies should differentiate between using AI to learn vs. using AI to cheat.",
            "I appreciate AI for helping me overcome writer's block and generate ideas to build upon.",
            "Schools need to adapt to the reality that AI is everywhere. Teaching ethical use is more practical than banning it.",
            "AI has made learning more accessible for students who struggle with traditional teaching methods.",
            "I use AI to get unstuck when I'm confused, then I work through the problem myself.",
            "The key is transparency - students should disclose when and how they use AI in their work.",
        ]

        # Create 100 survey responses directly (no separate SurveyUser table)
        for i in range(1, 101):
            username = f"student_{i:03d}"

            # Check if response already exists for this user_id
            existing_response = SurveyResponse.query.filter_by(user_id=i).first()
            if existing_response:
                continue

            # 85% say Yes to using AI, 15% say No
            uses_ai = "Yes" if random.random() < 0.85 else "No"

            # Random FRQ response
            frq = random.choice(frq_responses)

            # Create survey response with username directly
            response = SurveyResponse(
                user_id=i,
                username=username,
                uses_ai_schoolwork=uses_ai,
                policy_perspective=frq,
                badge_awarded=True
            )
            db.session.add(response)
            db.session.commit()

            # Create AI tool preferences for each subject using weighted random
            for subject, weights in subject_weights.items():
                ai_tool = random.choices(ai_tools, weights=weights, k=1)[0]
                preference = AIToolPreference(
                    response_id=response.id,
                    subject=subject,
                    ai_tool=ai_tool
                )
                db.session.add(preference)

            db.session.commit()

        print(f"Initialized {SurveyResponse.query.count()} survey responses")
