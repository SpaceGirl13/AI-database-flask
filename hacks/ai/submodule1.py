# submodule1.py - Flask Blueprint for AI Usage Survey
from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
from model.user import User
from flask import g

# Create Blueprint
survey_api = Blueprint('survey_api', __name__)

# Data file for storing survey responses
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
        
        return jsonify({
            'message': 'Survey submitted successfully',
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500