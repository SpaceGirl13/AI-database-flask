from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File to store survey data
DATA_FILE = 'survey_data.json'

def load_data():
    """Load survey data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize empty data structure
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
    """Save survey data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/api/survey', methods=['GET'])
def get_survey_data():
    """Get all survey data"""
    try:
        data = load_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    """Submit a new survey response"""
    try:
        # Get the form data from request
        form_data = request.json
        
        # Validate required fields
        required_fields = ['english', 'math', 'science', 'cs', 'history', 'useAI', 'frq']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Load existing data
        data = load_data()
        
        # Update counts for each subject
        data['english'][form_data['english']] += 1
        data['math'][form_data['math']] += 1
        data['science'][form_data['science']] += 1
        data['cs'][form_data['cs']] += 1
        data['history'][form_data['history']] += 1
        data['useAI'][form_data['useAI']] += 1
        
        # Add FRQ response with timestamp
        frq_entry = {
            'text': form_data['frq'],
            'timestamp': datetime.now().isoformat()
        }
        data['frqs'].insert(0, frq_entry)  # Add to beginning of list
        
        # Save updated data
        save_data(data)
        
        return jsonify({
            'message': 'Survey submitted successfully',
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey/recent-frqs', methods=['GET'])
def get_recent_frqs():
    """Get the 3 most recent FRQ responses"""
    try:
        data = load_data()
        recent_frqs = data['frqs'][:3]  # Get first 3 (most recent)
        return jsonify(recent_frqs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey/reset', methods=['POST'])
def reset_survey():
    """Reset all survey data (for testing purposes)"""
    try:
        initial_data = {
            'english': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'math': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'science': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'cs': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'history': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'useAI': {'Yes': 0, 'No': 0},
            'frqs': []
        }
        save_data(initial_data)
        return jsonify({'message': 'Survey data reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)