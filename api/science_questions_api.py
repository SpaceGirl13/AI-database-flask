# science_questions_api.py - Flask Blueprint for Science Practice Questions
from flask import Blueprint, request, jsonify
import json
import os

# Create Blueprint
science_questions_api = Blueprint('science_questions_api', __name__)

# Data file for storing questions
QUESTIONS_FILE = 'science_questions.json'

def load_questions():
    """Load questions from database file"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize with default science questions
        default_questions = {
            'questions': [
                {
                    'id': 1,
                    'question': 'Explain the process of photosynthesis in plants.',
                    'answer': 'Plants use light energy (usually from the sun) to convert carbon dioxide and water into glucose and oxygen through the chemical equation: 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂',
                    'prompt_template': 'Explain {question} Include the chemical equation, the role of chlorophyll, and the two main stages (light-dependent and light-independent reactions). Use clear examples.',
                    'category': 'biology'
                },
                {
                    'id': 2,
                    'question': 'What is Newton\'s Second Law of Motion?',
                    'answer': 'Force equals mass times acceleration (F = ma). The acceleration of an object depends on the net force acting on it and is inversely proportional to its mass.',
                    'prompt_template': 'Explain {question} Include the formula F = ma, provide real-world examples, and explain the relationship between force, mass, and acceleration step-by-step.',
                    'category': 'physics'
                },
                {
                    'id': 3,
                    'question': 'Describe the water cycle and its main stages.',
                    'answer': 'The water cycle includes evaporation (water turning to vapor), condensation (vapor forming clouds), precipitation (rain/snow falling), and collection (water gathering in bodies of water).',
                    'prompt_template': 'Describe {question} Explain each stage in detail: evaporation, condensation, precipitation, and collection. Include how energy from the sun drives the cycle.',
                    'category': 'earth-science'
                },
                {
                    'id': 4,
                    'question': 'What happens during a chemical reaction when vinegar and baking soda mix?',
                    'answer': 'An acid-base reaction occurs producing carbon dioxide gas (CO₂), water (H₂O), and sodium acetate. The chemical equation is: NaHCO₃ + CH₃COOH → CO₂ + H₂O + CH₃COONa',
                    'prompt_template': 'Explain {question} Include the chemical equation, identify the reactants and products, explain why bubbles form, and describe what type of reaction this is (acid-base reaction).',
                    'category': 'chemistry'
                }
            ]
        }
        save_questions(default_questions)
        return default_questions

def save_questions(data):
    """Save questions to database file"""
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@science_questions_api.route('/questions', methods=['GET'])
def get_questions():
    """Get all science questions, optionally filtered by topic"""
    try:
        questions_data = load_questions()
        topic = request.args.get('topic')

        print(f"[SCIENCE API] Received topic parameter: {topic}")
        print(f"[SCIENCE API] Request args: {request.args}")

        questions = questions_data['questions']
        print(f"[SCIENCE API] Total questions before filter: {len(questions)}")

        # Filter by topic if provided
        if topic:
            questions = [q for q in questions if q.get('category') == topic]
            print(f"[SCIENCE API] Questions after filtering by '{topic}': {len(questions)}")

        return jsonify({
            'success': True,
            'questions': questions,
            'debug_info': {
                'version': 'v2_with_filter',
                'topic_param': topic,
                'total_before_filter': len(questions_data['questions']),
                'total_after_filter': len(questions)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@science_questions_api.route('/questions/<int:question_id>', methods=['GET'])
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

@science_questions_api.route('/questions', methods=['POST'])
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
