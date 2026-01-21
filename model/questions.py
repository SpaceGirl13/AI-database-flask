""" Database models for Questions (Submodule 2) """
from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
import json
import os


class Question(db.Model):
    """
    Question Model

    Represents a question for submodule 2 (math or science subjects).

    Attributes:
        id (Column): Primary key, unique identifier for the question.
        _subject (Column): The subject area (math, science).
        _category (Column): The category within the subject (e.g., derivatives, biology).
        _question (Column): The question text.
        _answer (Column): The correct answer.
        _prompt_template (Column): Template for AI prompt generation.
    """
    __tablename__ = 'questions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    _subject = db.Column(db.String(50), nullable=False)
    _category = db.Column(db.String(50), nullable=False)
    _question = db.Column(db.Text, nullable=False)
    _answer = db.Column(db.Text, nullable=False)
    _prompt_template = db.Column(db.Text, nullable=True)

    def __init__(self, subject, category, question, answer, prompt_template=None):
        self._subject = subject
        self._category = category
        self._question = question
        self._answer = answer
        self._prompt_template = prompt_template

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, value):
        self._question = value

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value):
        self._answer = value

    @property
    def prompt_template(self):
        return self._prompt_template

    @prompt_template.setter
    def prompt_template(self, value):
        self._prompt_template = value

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
            "subject": self._subject,
            "category": self._category,
            "question": self._question,
            "answer": self._answer,
            "prompt_template": self._prompt_template
        }

    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self

        subject = inputs.get("subject", "")
        category = inputs.get("category", "")
        question = inputs.get("question", "")
        answer = inputs.get("answer", "")
        prompt_template = inputs.get("prompt_template", "")

        if subject:
            self._subject = subject
        if category:
            self._category = category
        if question:
            self._question = question
        if answer:
            self._answer = answer
        if prompt_template:
            self._prompt_template = prompt_template

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    @staticmethod
    def get_random_question(subject=None, category=None):
        """
        Get a random question, optionally filtered by subject and/or category.

        :param subject: Filter by subject (math, science)
        :param category: Filter by category (derivatives, biology, etc.)
        :return: A random Question object or None
        """
        query = Question.query
        if subject:
            query = query.filter_by(_subject=subject)
        if category:
            query = query.filter_by(_category=category)
        return query.order_by(func.random()).first()

    @staticmethod
    def get_random_questions(count=5, subject=None, category=None):
        """
        Get multiple random questions, optionally filtered by subject and/or category.

        :param count: Number of questions to return
        :param subject: Filter by subject (math, science)
        :param category: Filter by category (derivatives, biology, etc.)
        :return: A list of random Question objects
        """
        query = Question.query
        if subject:
            query = query.filter_by(_subject=subject)
        if category:
            query = query.filter_by(_category=category)
        return query.order_by(func.random()).limit(count).all()

    @staticmethod
    def get_all_by_subject(subject):
        """
        Get all questions for a specific subject.

        :param subject: The subject to filter by (math, science)
        :return: A list of Question objects
        """
        return Question.query.filter_by(_subject=subject).all()

    @staticmethod
    def get_all_by_category(category):
        """
        Get all questions for a specific category.

        :param category: The category to filter by
        :return: A list of Question objects
        """
        return Question.query.filter_by(_category=category).all()

    @staticmethod
    def get_categories(subject=None):
        """
        Get all unique categories, optionally filtered by subject.

        :param subject: Filter by subject (math, science)
        :return: A list of category names
        """
        query = db.session.query(Question._category).distinct()
        if subject:
            query = query.filter(Question._subject == subject)
        return [row[0] for row in query.all()]


"""Database Creation and Testing"""


def initQuestions():
    """Initialize questions database with data from JSON files"""
    with app.app_context():
        db.create_all()

        # Load math questions
        math_file = os.path.join(app.root_path, 'math_questions.json')
        if os.path.exists(math_file):
            with open(math_file, 'r') as f:
                math_data = json.load(f)
                for q in math_data.get('questions', []):
                    question = Question(
                        subject='math',
                        category=q.get('category', 'general'),
                        question=q.get('question', ''),
                        answer=q.get('answer', ''),
                        prompt_template=q.get('prompt_template', '')
                    )
                    try:
                        question.create()
                    except IntegrityError:
                        db.session.rollback()
                        print(f"Question already exists: {q.get('question', '')[:50]}")

        # Load science questions
        science_file = os.path.join(app.root_path, 'science_questions.json')
        if os.path.exists(science_file):
            with open(science_file, 'r') as f:
                science_data = json.load(f)
                for q in science_data.get('questions', []):
                    question = Question(
                        subject='science',
                        category=q.get('category', 'general'),
                        question=q.get('question', ''),
                        answer=q.get('answer', ''),
                        prompt_template=q.get('prompt_template', '')
                    )
                    try:
                        question.create()
                    except IntegrityError:
                        db.session.rollback()
                        print(f"Question already exists: {q.get('question', '')[:50]}")

        print("Questions database initialized successfully!")
