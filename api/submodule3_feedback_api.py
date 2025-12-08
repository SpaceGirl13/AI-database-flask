# submodule3_feedback_api.py - Flask Blueprint for Submodule 3 Feedback
from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

# Create Blueprint
submodule3_feedback_api = Blueprint('submodule3_feedback_api', __name__)

# Data file for storing feedback
FEEDBACK_FILE = 'submodule3_feedback.json'

def load_feedback():
    """Load feedback from database file"""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {'feedback': []}

def save_feedback(data):
    """Save feedback to database file"""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@submodule3_feedback_api.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for submodule 3"""
    try:
        feedback_data = request.json

        # Validate required fields
        required_fields = ['playerName', 'rating', 'category']
        for field in required_fields:
            if field not in feedback_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Add timestamp
        feedback_data['timestamp'] = datetime.now().isoformat()

        # Load existing feedback
        data = load_feedback()

        # Add new feedback to the beginning (most recent first)
        data['feedback'].insert(0, feedback_data)

        # Save back to file
        save_feedback(data)

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@submodule3_feedback_api.route('/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """Get the most recent feedback"""
    try:
        data = load_feedback()

        if not data['feedback']:
            return jsonify({
                'success': True,
                'feedback': None,
                'averageRating': 0,
                'totalResponses': 0
            }), 200

        # Calculate average rating
        ratings = [f['rating'] for f in data['feedback']]
        average_rating = sum(ratings) / len(ratings) if ratings else 0

        # Get most recent feedback
        recent = data['feedback'][0] if data['feedback'] else None

        return jsonify({
            'success': True,
            'feedback': recent,
            'averageRating': round(average_rating, 1),
            'totalResponses': len(data['feedback'])
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
