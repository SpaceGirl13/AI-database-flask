# submodule2.py - Flask Blueprint for Prompt Engineering Module
from flask import Blueprint, request, jsonify, current_app, g
import json
import os
from datetime import datetime
import random
import requests
from api.jwt_authorize import optional_token

# Create Blueprint
prompt_api = Blueprint('prompt_api', __name__)

# Data file for storing prompt history
DATA_FILE = 'instance/volumes/prompt_data.json'

def load_prompt_data():
    """Load prompt testing history"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'prompt_history': [], 'stats': {'total_prompts': 0, 'good_prompts': 0, 'bad_prompts': 0}}

def save_prompt_data(data):
    """Save prompt testing history"""
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

        return jsonify({
            'success': True,
            'prompt': prompt,
            'response': response,
            'type': prompt_type
        }), 200

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

# Helper functions
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
