# submodule2.py - Flask Blueprint for Prompt Engineering Module
from flask import Blueprint, request, jsonify, current_app, g
from datetime import datetime
import json
import os
import random
import requests
from api.jwt_authorize import optional_token, token_required
from model.user import User
from model.questions import Question

# Create Blueprint
prompt_api = Blueprint('prompt_api', __name__)

# Data file for storing prompt history
DATA_FILE = 'instance/volumes/prompt_data.json'

# Badge definitions (matching badge.py)
BADGE_DEFINITIONS = {
    'intelligent_instructor': {
        'name': 'Intelligent Instructor',
        'description': 'Crafted a high-quality, effective AI prompt',
        'requirement': 'Create a "Good" Prompt',
        'type': 'special',
        'image_url': 'https://github.com/user-attachments/assets/b1a7fc47-da59-4f14-a8d0-2b4c36df7cc5'
    },
    'perfect_prompt_engineer': {
        'name': 'Perfect Prompt Engineer',
        'description': 'Demonstrated expertise in crafting effective AI prompts',
        'requirement': 'Complete Submodule 2',
        'type': 'submodule',
        'image_url': 'https://github.com/user-attachments/assets/65a9a19a-4f0a-4e08-8a70-cd37c1e75b7d'
    }
}

def get_badge_info(badge_id):
    """Get complete badge information including image URL"""
    if badge_id in BADGE_DEFINITIONS:
        badge_info = BADGE_DEFINITIONS[badge_id].copy()
        badge_info['id'] = badge_id
        return badge_info
    return None

def load_prompt_data():
    """Load prompt testing history"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'prompt_history': [], 'stats': {'total_prompts': 0, 'good_prompts': 0, 'bad_prompts': 0}}

def save_prompt_data(data):
    """Save prompt testing history"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@prompt_api.route('/test', methods=['POST'])
@optional_token()
def test_prompt():
    """
    Test a prompt and return a simulated AI response
    Expects: { "prompt": "user's prompt text", "type": "good" | "bad" }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        prompt_type = data.get('type', 'unknown')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Generate simulated response based on prompt quality
        response = generate_simulated_response(prompt, prompt_type)

        # Get current user info
        user_id = g.current_user.uid if hasattr(g, 'current_user') and g.current_user else 'anonymous'
        user_name = g.current_user.name if hasattr(g, 'current_user') and g.current_user else 'Anonymous'

        # Save to history
        prompt_data = load_prompt_data()
        prompt_data['prompt_history'].append({
            'prompt': prompt,
            'type': prompt_type,
            'response': response,
            'user_id': user_id,
            'user_name': user_name,
            'timestamp': datetime.now().isoformat()
        })
        prompt_data['stats']['total_prompts'] += 1
        if prompt_type == 'good':
            prompt_data['stats']['good_prompts'] += 1
        elif prompt_type == 'bad':
            prompt_data['stats']['bad_prompts'] += 1

        save_prompt_data(prompt_data)

        # Award badge for creating a good prompt
        badge_awarded = False
        badge_info = None
        if prompt_type == 'good' and hasattr(g, 'current_user') and g.current_user:
            badge_id = 'intelligent_instructor'
            badge_awarded = g.current_user.add_badge(badge_id)
            if badge_awarded:
                badge_info = get_badge_info(badge_id)

        response_data = {
            'success': True,
            'prompt': prompt,
            'response': response,
            'type': prompt_type
        }
        
        if badge_awarded and badge_info:
            response_data['badge_awarded'] = badge_info

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/analyze', methods=['POST'])
def analyze_prompt():
    """
    Analyze a coding prompt and return quality metrics
    Expects: { "prompt": "coding prompt text" }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Analyze prompt quality
        analysis = perform_prompt_analysis(prompt)

        return jsonify({
            'success': True,
            'prompt': prompt,
            'analysis': analysis
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/improve', methods=['POST'])
def improve_prompt():
    """
    Improve a coding prompt
    Expects: { "prompt": "original prompt text" }
    """
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Generate improved version
        improved = generate_improved_prompt(prompt)

        return jsonify({
            'success': True,
            'original': prompt,
            'improved': improved
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/stats', methods=['GET'])
def get_stats():
    """Get prompt testing statistics"""
    try:
        prompt_data = load_prompt_data()
        return jsonify(prompt_data['stats']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/<prompt_type>', methods=['GET'])
def get_prompts_by_type(prompt_type):
    """
    Get prompts filtered by type (bad or good)
    Returns recent prompts for display in community feeds
    """
    try:
        prompt_data = load_prompt_data()

        # Filter prompts by type
        filtered_prompts = [
            {
                'prompt': p['prompt'],
                'timestamp': p['timestamp'],
                'response': p.get('response', ''),
                'user_id': p.get('user_id', 'anonymous'),
                'user_name': p.get('user_name', 'Anonymous')
            }
            for p in prompt_data['prompt_history']
            if p.get('type') == prompt_type
        ]

        # Return most recent 3 prompts
        return jsonify({
            'success': True,
            'prompts': filtered_prompts[-3:][::-1]  # Last 3, reversed (newest first)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_api.route('/survey', methods=['POST'])
def submit_science_survey():
    """
    Accepts JSON: { "topic": "biology" | "chemistry" | "physics" }
    Stores survey entry into DATA_FILE and returns redirectUrl for the client.
    """
    try:
        payload = request.get_json() or {}
        topic = (payload.get('topic') or '').strip().lower()

        if topic not in ('biology', 'chemistry', 'physics'):
            return jsonify(success=False, message='Invalid topic'), 400

        # Ensure data structure exists
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

        # Return a redirect URL which the frontend can follow
        redirect_map = {
            'biology': '/science/problems?topic=biology',
            'chemistry': '/science/problems?topic=chemistry',
            'physics': '/science/problems?topic=physics'
        }

        return jsonify(success=True, redirectUrl=redirect_map[topic]), 200

    except Exception as e:
        current_app.logger.exception('Error saving survey')
        return jsonify(success=False, error=str(e)), 500

@prompt_api.route('/complete', methods=['POST'])
@token_required()
def complete_submodule():
    """Mark submodule 2 as complete and award badge"""
    try:
        current_user = g.current_user
        badge_id = 'perfect_prompt_engineer'
        was_newly_awarded = current_user.add_badge(badge_id)

        # Always include badge info so UI can display it
        badge_info = get_badge_info(badge_id)

        response_data = {
            'success': True,
            'message': 'Submodule 2 completed!',
            'badge_awarded': was_newly_awarded,
            'badge': badge_info  # Always include badge info
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a separate blueprint to serve science questions at /api/science/questions
science_api = Blueprint('science_api', __name__, url_prefix='/api/science')

def _make_options_for_question(question_text, topic):
    """
    Build 4 prompt-options for a question:
      - One 'good' prompt: process/understanding-driven (requests step-by-step, explanations)
      - Three 'wrong' prompts: answer-driven (seek the final answer or short fact)
    Prompts are written to be similar in length.
    Returns (options_list, correct_index)
    """
    # Good prompt (process-focused)
    good = f"Explain step-by-step how to answer this: {question_text} Include the reasoning behind each step and why the result follows."

    # Wrong prompts (answer-focused); keep similar length to good prompt
    wrong1 = f"Give the direct answer to: {question_text} Provide the final result and a short statement only."
    wrong2 = f"State the main fact that answers: {question_text} Keep the response concise and focus on the conclusion."
    wrong3 = f"List the key result for: {question_text} Provide the single best answer without extra explanation."

    options = [good, wrong1, wrong2, wrong3]

    # Shuffle options but keep track of correct_index
    combined = list(enumerate(options))  # (index, text)
    random.shuffle(combined)
    shuffled_options = [text for (i, text) in combined]
    # find where original good prompt ended up
    correct_index = shuffled_options.index(good)

    return shuffled_options, correct_index

def generate_science_questions(topic, count=3):
    """
    Returns a list of question dicts for the given topic from the database.
    Each question dict includes:
      { id, category, question, prompt_template, answer, options, correct_index }
    """
    topic = topic.lower()

    # Get random questions from database
    db_questions = Question.get_random_questions(count=count, subject='science', category=topic)

    questions = []
    for q in db_questions:
        opts, correct_idx = _make_options_for_question(q.question, topic)
        # The answer is the good prompt (the one that teaches process-understanding)
        good_prompt = opts[correct_idx]
        question_obj = {
            'id': q.id,
            'category': q.category,
            'question': q.question,
            'prompt_template': q.prompt_template or f'Answer the following question step-by-step: {{question}}',
            'answer': good_prompt,            # the good AI prompt (process-understanding-driven)
            'options': opts,                  # list of 4 prompts (shuffled); one is 'good'
            'correct_index': correct_idx      # index into options which is the good prompt
        }
        questions.append(question_obj)

    return questions

@science_api.route('/questions', methods=['GET'])
def get_science_questions():
    """
    Returns random science questions from the database.
    Query: ?topic=biology|chemistry|physics&count=3
    Response example:
      { success: True, questions: [ {id, category, question, prompt_template, answer, options, correct_index}, ... ] }
    """
    try:
        topic = request.args.get('topic', '').strip().lower()
        count = request.args.get('count', 3, type=int)

        if topic not in ('biology', 'chemistry', 'physics'):
            topic = 'biology'

        print(f"[SCIENCE API] Topic: {topic}, Count: {count}")
        questions = generate_science_questions(topic, count)
        print(f"[SCIENCE API] Returning {len(questions)} questions")

        return jsonify(success=True, questions=questions), 200

    except Exception as e:
        current_app.logger.exception('Error generating science questions')
        return jsonify(success=False, error=str(e)), 500


@science_api.route('/categories', methods=['GET'])
def get_science_categories():
    """Get all available science question categories"""
    try:
        categories = Question.get_categories(subject='science')
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_simulated_response(prompt, prompt_type):
    """Generate AI response using Gemini API"""
    from __init__ import app

    # Get Gemini API configuration
    api_key = app.config.get('GEMINI_API_KEY')
    server = app.config.get('GEMINI_SERVER')

    # If Gemini is not configured, return error message
    if not api_key or not server:
        return "Error: Gemini API not configured. Please contact your administrator."

    try:
        # Build the endpoint URL
        endpoint = f"{server}?key={api_key}"

        # Prepare the request payload for Gemini API
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        # Make request to Gemini API
        response = requests.post(
            endpoint,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            # Extract the generated text
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            return generated_text
        else:
            # Log the error details
            error_details = response.text
            current_app.logger.error(f"Gemini API error {response.status_code}: {error_details}")
            return f"Error: Gemini API returned status {response.status_code}. Details: {error_details[:200]}"

    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API: {e}")
        return f"Error: Could not generate response. {str(e)}"

def perform_prompt_analysis(prompt):
    """Analyze coding prompt quality"""
    checklist = []
    score = 0

    # Check for programming language
    languages = ['python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust', 'html', 'css']
    has_language = any(lang in prompt.lower() for lang in languages)
    checklist.append({
        'item': 'Specifies programming language',
        'passed': has_language
    })
    if has_language:
        score += 25

    # Check for specific action
    actions = ['explain', 'debug', 'create', 'write', 'help', 'show', 'fix', 'build', 'implement']
    has_action = any(action in prompt.lower() for action in actions)
    checklist.append({
        'item': 'Uses clear action verb',
        'passed': has_action
    })
    if has_action:
        score += 25

    # Check for details
    has_details = len(prompt) > 20
    checklist.append({
        'item': 'Includes sufficient detail',
        'passed': has_details
    })
    if has_details:
        score += 25

    # Check for context
    context_words = ['beginner', 'simple', 'step-by-step', 'example', 'comments', 'for', 'with']
    has_context = any(word in prompt.lower() for word in context_words)
    checklist.append({
        'item': 'Provides context or level',
        'passed': has_context
    })
    if has_context:
        score += 25

    return {
        'checklist': checklist,
        'score': score,
        'total': 100
    }

def generate_improved_prompt(prompt):
    """Generate an improved version of a coding prompt"""
    improved = prompt

    # Add language if missing
    languages = ['python', 'javascript', 'java', 'c++']
    has_language = any(lang in improved.lower() for lang in languages)
    if not has_language:
        improved = f"In Python, {improved.lower()}"

    # Add detail if too short
    if len(improved) < 30:
        improved += " with step-by-step explanation and examples"

    # Add context if missing
    context_words = ['beginner', 'simple', 'example']
    has_context = any(word in improved.lower() for word in context_words)
    if not has_context:
        improved += ". Explain it in simple terms for beginners."

    # Ensure it starts with capital letter
    improved = improved[0].upper() + improved[1:] if improved else improved

    # Ensure it ends with period
    if improved and not improved.endswith('.'):
        improved += '.'

    return improved