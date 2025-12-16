# coding_questions_api.py - Flask Blueprint for Coding Practice Questions
from flask import Blueprint, request, jsonify
import json
import os

# Create Blueprint
coding_questions_api = Blueprint('coding_questions_api', __name__)

# Data file for storing questions
QUESTIONS_FILE = 'coding_questions.json'

def load_questions():
    """Load questions from database file"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"fill_in_blank": [], "write_code": []}

@coding_questions_api.route('/fill-in-blank', methods=['GET'])
def get_fill_in_blank():
    """Get fill-in-the-blank questions"""
    try:
        questions_data = load_questions()
        language = request.args.get('language')

        questions = questions_data.get('fill_in_blank', [])

        if language:
            questions = [q for q in questions if q.get('language') == language]

        return jsonify({
            'success': True,
            'questions': questions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@coding_questions_api.route('/write-code', methods=['GET'])
def get_write_code():
    """Get write-code-from-scratch questions"""
    try:
        questions_data = load_questions()
        language = request.args.get('language')

        questions = questions_data.get('write_code', [])

        if language:
            questions = [q for q in questions if q.get('language') == language]

        return jsonify({
            'success': True,
            'questions': questions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
