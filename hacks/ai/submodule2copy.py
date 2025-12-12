# submodule2copy.py - Flask Blueprint for Prompt Engineering Module
from flask import Blueprint, request, jsonify, current_app, g
from datetime import datetime
import json
import os
import random
import requests
from api.jwt_authorize import optional_token

# Create Blueprint
prompt_api = Blueprint('prompt_api', __name__)

# Data file for storing prompt history and survey/results
DATA_FILE = 'instance/volumes/prompt_data.json'

# Ensure data directory exists and initialize file if missing
def _ensure_data_file():
    dirpath = os.path.dirname(DATA_FILE)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        initial = {
            'prompt_history': [], 
            'stats': {'total_prompts': 0, 'good_prompts': 0, 'bad_prompts': 0}, 
            'science_survey': [], 
            'science_results': [],
            'math_survey': []
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(initial, f, indent=2)

_ensure_data_file()

def load_prompt_data():
    """Load prompt testing history"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'prompt_history': [], 
        'stats': {'total_prompts': 0, 'good_prompts': 0, 'bad_prompts': 0}, 
        'science_survey': [], 
        'science_results': [],
        'math_survey': []
    }

def save_prompt_data(data):
    """Save prompt testing history"""
    data.setdefault('prompt_history', [])
    data.setdefault('stats', {'total_prompts': 0, 'good_prompts': 0, 'bad_prompts': 0})
    data.setdefault('science_survey', [])
    data.setdefault('science_results', [])
    data.setdefault('math_survey', [])
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@prompt_api.route('/test', methods=['POST'])
@optional_token()
def test_prompt():
    """Test a prompt and return AI response"""
    try:
        data = request.json or {}
        prompt = data.get('prompt', '').strip()
        prompt_type = data.get('type', 'unknown')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        response = generate_simulated_response(prompt, prompt_type)
        user_id = getattr(getattr(g, 'current_user', None), 'uid', 'anonymous')
        user_name = getattr(getattr(g, 'current_user', None), 'name', 'Anonymous')

        prompt_data = load_prompt_data()
        prompt_data['prompt_history'].append({
            'prompt': prompt,
            'type': prompt_type,
            'response': response,
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': datetime.now().isoformat()
        })
        prompt_data['stats']['total_prompts'] = prompt_data.get('stats', {}).get('total_prompts', 0) + 1
        if prompt_type == 'good':
            prompt_data['stats']['good_prompts'] = prompt_data['stats'].get('good_prompts', 0) + 1
        elif prompt_type == 'bad':
            prompt_data['stats']['bad_prompts'] = prompt_data['stats'].get('bad_prompts', 0) + 1

        save_prompt_data(prompt_data)

        return jsonify({
            'success': True,
            'prompt': prompt,
            'response': response,
            'type': prompt_type
        }), 200

    except Exception as e:
        current_app.logger.exception('test_prompt error')
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/analyze', methods=['POST'])
def analyze_prompt():
    """Analyze coding prompt quality"""
    try:
        data = request.json or {}
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        analysis = perform_prompt_analysis(prompt)

        return jsonify({
            'success': True,
            'prompt': prompt,
            'analysis': analysis
        }), 200

    except Exception as e:
        current_app.logger.exception('analyze_prompt error')
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/improve', methods=['POST'])
def improve_prompt():
    """Improve a coding prompt"""
    try:
        data = request.json or {}
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        improved = generate_improved_prompt(prompt)

        return jsonify({
            'success': True,
            'original': prompt,
            'improved': improved
        }), 200

    except Exception as e:
        current_app.logger.exception('improve_prompt error')
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/stats', methods=['GET'])
def get_stats():
    """Get prompt testing statistics"""
    try:
        prompt_data = load_prompt_data()
        return jsonify(prompt_data.get('stats', {})), 200
    except Exception as e:
        current_app.logger.exception('get_stats error')
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/<prompt_type>', methods=['GET'])
def get_prompts_by_type(prompt_type):
    """Get prompts filtered by type"""
    try:
        prompt_data = load_prompt_data()

        filtered_prompts = [
            {
                'prompt': p['prompt'],
                'timestamp': p['timestamp'],
                'response': p.get('response', ''),
                'user_id': p.get('user_id', 'anonymous'),
                'user_name': p.get('user_name', 'Anonymous')
            }
            for p in prompt_data.get('prompt_history', [])
            if p.get('type') == prompt_type
        ]

        return jsonify({
            'success': True,
            'prompts': filtered_prompts[-3:][::-1]
        }), 200

    except Exception as e:
        current_app.logger.exception('get_prompts_by_type error')
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/survey', methods=['POST'])
@optional_token()
def submit_science_survey():
    """Store science topic selection"""
    try:
        payload = request.get_json() or {}
        topic = (payload.get('topic') or '').strip().lower()

        if topic not in ('biology', 'chemistry', 'physics'):
            return jsonify(success=False, message='Invalid topic'), 400

        data = load_prompt_data()
        if 'science_survey' not in data:
            data['science_survey'] = []

        user_obj = getattr(g, 'current_user', None)
        user_id = getattr(user_obj, 'uid', 'anonymous') if user_obj else 'anonymous'
        user_name = getattr(user_obj, 'name', user_id) if user_obj else 'Anonymous'

        entry = {
            'topic': topic,
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': datetime.utcnow().isoformat()
        }

        data['science_survey'].append(entry)
        save_prompt_data(data)

        return jsonify({
            'success': True,
            'topic': topic,
            'message': f"Saved survey selection for {topic}."
        }), 200

    except Exception as e:
        current_app.logger.exception('Error saving survey')
        return jsonify(success=False, error=str(e)), 500

# Math API Blueprint
math_api = Blueprint('math_api', __name__, url_prefix='/api/math')

def generate_math_questions(topic):
    """Generate 6 questions for the selected math topic"""
    topic = topic.lower()
    
    banks = {
        'derivatives': [
            {
                'question': 'Find the derivative of f(x) = 3x⁴ - 2x³ + 5x - 7',
                'answer': "f'(x) = 12x³ - 6x² + 5"
            },
            {
                'question': 'Find the derivative of f(x) = (2x + 1)(x² - 3)',
                'answer': "f'(x) = 2(x² - 3) + (2x + 1)(2x) = 6x² + 2x - 6"
            },
            {
                'question': 'Find the derivative of f(x) = sin(x) + cos(x)',
                'answer': "f'(x) = cos(x) - sin(x)"
            },
            {
                'question': 'Find the derivative of f(x) = e^(2x)',
                'answer': "f'(x) = 2e^(2x) using the chain rule"
            },
            {
                'question': 'Find the derivative of f(x) = ln(x²)',
                'answer': "f'(x) = 2/x using the chain rule"
            },
            {
                'question': 'Find the derivative of f(x) = x³/x²',
                'answer': "First simplify to f(x) = x, then f'(x) = 1"
            }
        ],
        'fractions': [
            {
                'question': 'Add: 2/3 + 1/4',
                'answer': '8/12 + 3/12 = 11/12'
            },
            {
                'question': 'Subtract: 5/6 - 1/3',
                'answer': '5/6 - 2/6 = 3/6 = 1/2'
            },
            {
                'question': 'Multiply: 3/4 × 2/5',
                'answer': '6/20 = 3/10'
            },
            {
                'question': 'Divide: 2/3 ÷ 4/5',
                'answer': '2/3 × 5/4 = 10/12 = 5/6'
            },
            {
                'question': 'Simplify: 12/18',
                'answer': '2/3 (divide both by GCD of 6)'
            },
            {
                'question': 'Convert to mixed number: 11/4',
                'answer': '2 3/4'
            }
        ],
        'trig': [
            {
                'question': 'Find sin(30°)',
                'answer': '1/2'
            },
            {
                'question': 'Find cos(60°)',
                'answer': '1/2'
            },
            {
                'question': 'Find tan(45°)',
                'answer': '1'
            },
            {
                'question': 'If sin(θ) = 3/5, find cos(θ) in a right triangle',
                'answer': 'cos(θ) = 4/5 using Pythagorean theorem'
            },
            {
                'question': 'Simplify: sin²(x) + cos²(x)',
                'answer': '1 (Pythagorean identity)'
            },
            {
                'question': 'Find the period of y = sin(2x)',
                'answer': 'π (period is 2π/2 = π)'
            }
        ]
    }

    selected_bank = banks.get(topic, banks['derivatives'])
    questions = []
    
    for q in selected_bank:
        question_obj = {
            'id': random.randint(100000, 999999),
            'category': topic,
            'question': q['question'],
            'prompt_template': 'Solve this step-by-step, showing all work and explaining each step: {question}',
            'answer': q['answer']
        }
        questions.append(question_obj)

    return questions

@math_api.route('/questions', methods=['GET'])
def get_math_questions():
    """Get 6 math questions for selected topic"""
    try:
        topic = request.args.get('topic', '').strip().lower()
        if topic not in ('derivatives', 'fractions', 'trig'):
            topic = 'derivatives'

        questions = generate_math_questions(topic)
        return jsonify(success=True, questions=questions), 200

    except Exception as e:
        current_app.logger.exception('Error generating math questions')
        return jsonify(success=False, error=str(e)), 500

@math_api.route('/survey', methods=['POST'])
@optional_token()
def submit_math_survey():
    """Store math topic selection"""
    try:
        payload = request.get_json() or {}
        topic = (payload.get('topic') or '').strip().lower()

        if topic not in ('derivatives', 'fractions', 'trig'):
            return jsonify(success=False, message='Invalid topic'), 400

        data = load_prompt_data()
        if 'math_survey' not in data:
            data['math_survey'] = []

        user_obj = getattr(g, 'current_user', None)
        user_id = getattr(user_obj, 'uid', 'anonymous') if user_obj else 'anonymous'
        user_name = getattr(user_obj, 'name', user_id) if user_obj else 'Anonymous'

        entry = {
            'topic': topic,
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': datetime.utcnow().isoformat()
        }

        data['math_survey'].append(entry)
        save_prompt_data(data)

        return jsonify({
            'success': True,
            'topic': topic,
            'message': f"Saved survey selection for {topic}."
        }), 200

    except Exception as e:
        current_app.logger.exception('Error saving math survey')
        return jsonify(success=False, error=str(e)), 500

# Science API Blueprint
science_api = Blueprint('science_api', __name__, url_prefix='/api/science')

def generate_science_questions(topic):
    """Generate 4 high school level questions for the selected topic"""
    topic = topic.lower()
    
    banks = {
        'biology': [
            {
                'question': 'Explain the process of photosynthesis including the light and dark reactions.',
                'answer': 'Photosynthesis converts light energy into chemical energy. Light reactions in thylakoids produce ATP and NADPH, while dark reactions (Calvin cycle) use these to fix CO2 into glucose.'
            },
            {
                'question': 'Describe the process of cellular respiration and name where it occurs.',
                'answer': 'Cellular respiration occurs in the mitochondria and involves glycolysis, the Krebs cycle, and the electron transport chain to produce ATP from glucose.'
            },
            {
                'question': 'What are the main differences between prokaryotic and eukaryotic cells?',
                'answer': 'Prokaryotic cells lack a nucleus and membrane-bound organelles, while eukaryotic cells have both. Prokaryotes are typically smaller and simpler.'
            },
            {
                'question': 'Explain the difference between mitosis and meiosis.',
                'answer': 'Mitosis produces two identical diploid cells for growth and repair. Meiosis produces four haploid gametes with genetic variation for sexual reproduction.'
            }
        ],
        'chemistry': [
            {
                'question': 'Explain the difference between ionic and covalent bonding.',
                'answer': 'Ionic bonding involves transfer of electrons between atoms (metal to non-metal), while covalent bonding involves sharing of electrons between non-metal atoms.'
            },
            {
                'question': 'What is pH and how does it relate to H+ concentration?',
                'answer': 'pH is a measure of acidity/basicity. It is the negative logarithm of H+ concentration. Lower pH means higher H+ concentration (acidic), higher pH means lower H+ (basic).'
            },
            {
                'question': 'Explain the difference between exothermic and endothermic reactions.',
                'answer': 'Exothermic reactions release energy to surroundings (negative ΔH), while endothermic reactions absorb energy from surroundings (positive ΔH).'
            },
            {
                'question': 'What are the different types of chemical reactions and give an example of each.',
                'answer': 'Main types: synthesis (A+B→AB), decomposition (AB→A+B), single replacement (A+BC→AC+B), double replacement (AB+CD→AD+CB), and combustion (fuel+O2→CO2+H2O).'
            }
        ],
        'physics': [
            {
                'question': "State Newton's three laws of motion and give a short example for each.",
                'answer': "1st: Object at rest stays at rest (book on table). 2nd: F=ma (pushing a cart). 3rd: Action-reaction pairs (rocket propulsion)."
            },
            {
                'question': 'Explain the difference between kinetic and potential energy.',
                'answer': 'Kinetic energy is energy of motion (KE = ½mv²), while potential energy is stored energy due to position or configuration (gravitational PE = mgh).'
            },
            {
                'question': "What is Ohm's law and what does it relate?",
                'answer': "Ohm's law states V = IR, relating voltage (V), current (I), and resistance (R) in electrical circuits."
            },
            {
                'question': 'Explain the difference between speed, velocity, and acceleration.',
                'answer': 'Speed is scalar (magnitude only). Velocity is vector (magnitude and direction). Acceleration is rate of change of velocity, also a vector.'
            }
        ]
    }

    selected_bank = banks.get(topic, banks['biology'])
    questions = []
    
    for q in selected_bank:
        question_obj = {
            'id': random.randint(100000, 999999),
            'category': topic,
            'question': q['question'],
            'prompt_template': 'Explain the following to a high school student with clear examples and step-by-step reasoning: {question}',
            'answer': q['answer']
        }
        questions.append(question_obj)

    return questions

@science_api.route('/questions', methods=['GET'])
def get_science_questions():
    """Get 4 science questions for selected topic"""
    try:
        topic = request.args.get('topic', '').strip().lower()
        if topic not in ('biology', 'chemistry', 'physics'):
            topic = 'biology'

        questions = generate_science_questions(topic)
        return jsonify(success=True, questions=questions), 200

    except Exception as e:
        current_app.logger.exception('Error generating science questions')
        return jsonify(success=False, error=str(e)), 500

@science_api.route('/submit_answers', methods=['POST'])
@optional_token()
def submit_science_answers():
    """Store science quiz results"""
    try:
        payload = request.get_json() or {}
        topic = (payload.get('topic') or '').strip().lower()
        answers = payload.get('answers', [])
        
        if topic not in ('biology', 'chemistry', 'physics'):
            return jsonify(success=False, message='Invalid topic'), 400

        user_obj = getattr(g, 'current_user', None)
        user_id = getattr(user_obj, 'uid', payload.get('user_id', 'anonymous')) if user_obj else payload.get('user_id', 'anonymous')
        user_name = getattr(user_obj, 'name', payload.get('user_name', user_id)) if user_obj else payload.get('user_name', 'Anonymous')

        entry = {
            'topic': topic,
            'user_id': user_id,
            'user_name': user_name,
            'answers': answers,
            'timestamp': datetime.utcnow().isoformat()
        }

        data = load_prompt_data()
        if 'science_results' not in data:
            data['science_results'] = []
        data['science_results'].append(entry)
        save_prompt_data(data)

        score = sum(1 for a in answers if a.get('selected_index') == a.get('correct_index'))

        return jsonify(success=True, saved=True, score=score, total=len(answers)), 200

    except Exception as e:
        current_app.logger.exception('Error saving answers')
        return jsonify(success=False, error=str(e)), 500

# Helper Functions
def generate_simulated_response(prompt, prompt_type):
    """Generate AI response using Gemini API"""
    try:
        from __init__ import app
    except Exception:
        app = current_app

    api_key = app.config.get('GEMINI_API_KEY')
    server = app.config.get('GEMINI_SERVER')

    if not api_key or not server:
        return "Error: Gemini API not configured. Please contact your administrator."

    try:
        endpoint = f"{server}?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(
            endpoint,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            return generated_text
        else:
            error_details = response.text
            current_app.logger.error(f"Gemini API error {response.status_code}: {error_details}")
            return f"Error: Gemini API returned status {response.status_code}."

    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API: {e}")
        return f"Error: Could not generate response. {str(e)}"

def perform_prompt_analysis(prompt):
    """Analyze coding prompt quality"""
    checklist = []
    score = 0

    languages = ['python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust', 'html', 'css']
    has_language = any(lang in prompt.lower() for lang in languages)
    checklist.append({'item': 'Specifies programming language', 'passed': has_language})
    if has_language:
        score += 25

    actions = ['explain', 'debug', 'create', 'write', 'help', 'show', 'fix', 'build', 'implement']
    has_action = any(action in prompt.lower() for action in actions)
    checklist.append({'item': 'Uses clear action verb', 'passed': has_action})
    if has_action:
        score += 25

    has_details = len(prompt) > 20
    checklist.append({'item': 'Includes sufficient detail', 'passed': has_details})
    if has_details:
        score += 25

    context_words = ['beginner', 'simple', 'step-by-step', 'example', 'comments', 'for', 'with']
    has_context = any(word in prompt.lower() for word in context_words)
    checklist.append({'item': 'Provides context or level', 'passed': has_context})
    if has_context:
        score += 25

    return {'checklist': checklist, 'score': score, 'total': 100}

def generate_improved_prompt(prompt):
    """Generate improved version of coding prompt"""
    improved = prompt

    languages = ['python', 'javascript', 'java', 'c++']
    has_language = any(lang in improved.lower() for lang in languages)
    if not has_language:
        improved = f"In Python, {improved.lower()}"

    if len(improved) < 30:
        improved += " with step-by-step explanation and examples"

    context_words = ['beginner', 'simple', 'example']
    has_context = any(word in improved.lower() for word in context_words)
    if not has_context:
        improved += ". Explain it in simple terms for beginners."

    improved = improved[0].upper() + improved[1:] if improved else improved

    if improved and not improved.endswith('.'):
        improved += '.'

    return improved