# math_questions_api.py - Flask Blueprint for Math Practice Questions
from flask import Blueprint, request, jsonify
import json
import os

# Create Blueprint
math_questions_api = Blueprint('math_questions_api', __name__)

# Data file for storing questions
QUESTIONS_FILE = 'math_questions.json'

def load_questions():
    """Load questions from database file"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize with default derivative questions
        default_questions = {
            'questions': [
                {
                    'id': 1,
                    'question': 'What is the derivative of 3x⁴ - 2x³?',
                    'answer': '12x³ - 6x²',
                    'prompt_template': 'Find the derivative of {question} step-by-step. Show all work and explain each step using the power rule.',
                    'category': 'derivatives'
                },
                {
                    'id': 2,
                    'question': 'Find the derivative of sin(x) + cos(x)',
                    'answer': 'cos(x) - sin(x)',
                    'prompt_template': 'Calculate the derivative of {question}. Explain the derivatives of trigonometric functions and show your work.',
                    'category': 'derivatives'
                },
                {
                    'id': 3,
                    'question': 'What is the derivative of e^(2x)?',
                    'answer': '2e^(2x)',
                    'prompt_template': 'Find the derivative of {question}. Use the chain rule and explain each step clearly.',
                    'category': 'derivatives'
                },
                {
                    'id': 4,
                    'question': 'Find the derivative of ln(x²)',
                    'answer': '2/x',
                    'prompt_template': 'Calculate the derivative of {question} step-by-step. Apply the chain rule and logarithm properties.',
                    'category': 'derivatives'
                }
            ]
        }
        save_questions(default_questions)
        return default_questions

def save_questions(data):
    """Save questions to database file"""
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@math_questions_api.route('/questions', methods=['GET'])
def get_questions():
    """Get all math questions"""
    try:
        questions_data = load_questions()
        return jsonify({
            'success': True,
            'questions': questions_data['questions']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@math_questions_api.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """Get a specific question by ID"""
    try:
        questions_data = load_questions()
        question = next((q for q in questions_data['questions'] if q['id'] == question_id), None)

        if question:
            return jsonify({
                'success': True,
                'question': question
            }), 200
        else:
            return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@math_questions_api.route('/questions', methods=['POST'])
def add_question():
    """Add a new question to the database"""
    try:
        question_data = request.json

        # Validate required fields
        required_fields = ['question', 'answer', 'prompt_template', 'category']
        for field in required_fields:
            if field not in question_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Load existing questions
        data = load_questions()

        # Generate new ID
        max_id = max([q['id'] for q in data['questions']], default=0)
        question_data['id'] = max_id + 1

        # Add new question
        data['questions'].append(question_data)

        # Save back to file
        save_questions(data)

        return jsonify({
            'success': True,
            'message': 'Question added successfully',
            'question': question_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
