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
        # Initialize with default questions for derivatives, fractions, and trig
        default_questions = {
            'questions': [
                # Derivatives
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
                },
                # Fractions
                {
                    'id': 5,
                    'question': 'Simplify: (3/4) + (2/3)',
                    'answer': '17/12 or 1 5/12',
                    'prompt_template': 'Solve {question}. Show all steps including finding the common denominator and simplifying.',
                    'category': 'fractions'
                },
                {
                    'id': 6,
                    'question': 'What is (5/6) × (4/15)?',
                    'answer': '2/9',
                    'prompt_template': 'Calculate {question} step-by-step. Show the multiplication and simplification process.',
                    'category': 'fractions'
                },
                {
                    'id': 7,
                    'question': 'Divide: (3/8) ÷ (9/16)',
                    'answer': '2/3',
                    'prompt_template': 'Solve {question}. Explain the process of dividing fractions using the reciprocal method.',
                    'category': 'fractions'
                },
                {
                    'id': 8,
                    'question': 'Simplify: (2/5) - (1/3)',
                    'answer': '1/15',
                    'prompt_template': 'Calculate {question}. Show how to find the common denominator and subtract the fractions.',
                    'category': 'fractions'
                },
                # Trigonometry
                {
                    'id': 9,
                    'question': 'What is sin(30°)?',
                    'answer': '1/2 or 0.5',
                    'prompt_template': 'Find {question}. Explain using the unit circle or special right triangles.',
                    'category': 'trig'
                },
                {
                    'id': 10,
                    'question': 'Calculate cos(60°)',
                    'answer': '1/2 or 0.5',
                    'prompt_template': 'Determine {question}. Use the unit circle and explain the relationship to the 30-60-90 triangle.',
                    'category': 'trig'
                },
                {
                    'id': 11,
                    'question': 'What is tan(45°)?',
                    'answer': '1',
                    'prompt_template': 'Find {question}. Explain using the definition of tangent and the 45-45-90 triangle.',
                    'category': 'trig'
                },
                {
                    'id': 12,
                    'question': 'Simplify: sin²(x) + cos²(x)',
                    'answer': '1',
                    'prompt_template': 'Simplify {question}. Explain the Pythagorean identity and its proof.',
                    'category': 'trig'
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
    """Get all math questions, optionally filtered by topic"""
    try:
        questions_data = load_questions()

        # Check if topic filter is provided
        topic = request.args.get('topic')
        print(f"[MATH API] Topic parameter received: {topic}")
        print(f"[MATH API] Total questions in DB: {len(questions_data['questions'])}")

        if topic:
            # Filter questions by topic
            filtered_questions = [q for q in questions_data['questions'] if q.get('category') == topic]
            print(f"[MATH API] Filtering by topic: {topic}")
            print(f"[MATH API] Filtered questions count: {len(filtered_questions)}")
            print(f"[MATH API] All categories in DB: {[q.get('category') for q in questions_data['questions']]}")
            return jsonify({
                'success': True,
                'questions': filtered_questions,
                'topic': topic
            }), 200
        else:
            # Return all questions
            print(f"[MATH API] No topic filter - returning all questions")
            return jsonify({
                'success': True,
                'questions': questions_data['questions']
            }), 200
    except Exception as e:
        print(f"[MATH API] Error: {str(e)}")
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
