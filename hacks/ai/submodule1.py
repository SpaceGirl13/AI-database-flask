# submodule1.py - Enhanced with badges
from flask import Blueprint, request, jsonify, session
import json
import os
from datetime import datetime
from badge_service import BadgeService

survey_api = Blueprint('survey_api', __name__)
badge_service = BadgeService()

DATA_FILE = 'survey_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            'english': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'math': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'science': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'cs': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'history': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'useAI': {'Yes': 0, 'No': 0},
            'frqs': []
        }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@survey_api.route('/survey', methods=['GET'])
def get_survey_data():
    try:
        data = load_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@survey_api.route('/survey', methods=['POST'])
def submit_survey():
    try:
        form_data = request.json
        
        # Check if user is logged in
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not authenticated'}), 401
        
        required_fields = ['english', 'math', 'science', 'cs', 'history', 'useAI', 'frq']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        data = load_data()
        
        data['english'][form_data['english']] += 1
        data['math'][form_data['math']] += 1
        data['science'][form_data['science']] += 1
        data['cs'][form_data['cs']] += 1
        data['history'][form_data['history']] += 1
        data['useAI'][form_data['useAI']] += 1
        
        frq_entry = {
            'text': form_data['frq'],
            'timestamp': datetime.now().isoformat()
        }
        data['frqs'].insert(0, frq_entry)
        
        save_data(data)
        
        # Award badges
        badge_results = []
        
        # Award Sensational Surveyor badge for completing survey
        surveyor_badge = badge_service.award_badge(username, 'sensational_surveyor')
        if surveyor_badge['success']:
            badge_results.append(surveyor_badge)
        
        # Award Delightful Data Scientist badge for completing submodule 1
        scientist_badge = badge_service.award_badge(username, 'delightful_data_scientist')
        if scientist_badge['success']:
            badge_results.append(scientist_badge)
        
        return jsonify({
            'message': 'Survey submitted successfully',
            'data': data,
            'badges': badge_results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@survey_api.route('/survey/completion-status', methods=['GET'])
def check_completion():
    """Check if user completed this submodule"""
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not authenticated'}), 401
        
        completed = badge_service.has_badge(username, 'delightful_data_scientist')
        
        return jsonify({'completed': completed}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500