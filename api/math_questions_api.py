# math_questions_api.py - Flask Blueprint for Math Practice Questions
from flask import Blueprint, request, jsonify
from model.questions import Question

# Create Blueprint
math_questions_api = Blueprint('math_questions_api', __name__)


@math_questions_api.route('/questions', methods=['GET'])
def get_questions():
    """Get random math questions from database, optionally filtered by topic/category"""
    try:
        # Check if topic filter is provided
        topic = request.args.get('topic')
        count = request.args.get('count', 4, type=int)  # Default to 4 questions

        print(f"[MATH API] Topic parameter received: {topic}")
        print(f"[MATH API] Count parameter: {count}")

        if topic:
            # Get random questions filtered by category
            questions = Question.get_random_questions(count=count, subject='math', category=topic)
            print(f"[MATH API] Filtering by topic: {topic}")
        else:
            # Get random questions for all math categories
            questions = Question.get_random_questions(count=count, subject='math')
            print(f"[MATH API] No topic filter - returning random math questions")

        # Convert to list of dicts
        questions_data = [q.read() for q in questions]
        print(f"[MATH API] Questions count: {len(questions_data)}")

        return jsonify({
            'success': True,
            'questions': questions_data,
            'topic': topic
        }), 200

    except Exception as e:
        print(f"[MATH API] Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@math_questions_api.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """Get a specific question by ID"""
    try:
        question = Question.query.get(question_id)

        if question and question.subject == 'math':
            return jsonify({
                'success': True,
                'question': question.read()
            }), 200
        else:
            return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@math_questions_api.route('/questions', methods=['POST'])
def add_question():
    """Add a new math question to the database"""
    try:
        question_data = request.json

        # Validate required fields
        required_fields = ['question', 'answer', 'prompt_template', 'category']
        for field in required_fields:
            if field not in question_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create new question
        question = Question(
            subject='math',
            category=question_data['category'],
            question=question_data['question'],
            answer=question_data['answer'],
            prompt_template=question_data['prompt_template']
        )
        question.create()

        return jsonify({
            'success': True,
            'message': 'Question added successfully',
            'question': question.read()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@math_questions_api.route('/categories', methods=['GET'])
def get_categories():
    """Get all available math question categories"""
    try:
        categories = Question.get_categories(subject='math')
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
