# badge_api.py
from flask import Blueprint, jsonify, session
from badge_service import BadgeService
from badges_config import BADGES

badge_api = Blueprint('badge_api', __name__)
badge_service = BadgeService()

@badge_api.route('/badges', methods=['GET'])
def get_all_badges():
    """Get all available badges"""
    return jsonify({'badges': list(BADGES.values())}), 200

@badge_api.route('/badges/user', methods=['GET'])
def get_user_badges():
    """Get badges earned by the current user"""
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not authenticated'}), 401
        
        badges = badge_service.get_user_badges(username)
        return jsonify({'badges': badges}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@badge_api.route('/badges/progress', methods=['GET'])
def get_user_progress():
    """Get user progress and statistics"""
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not authenticated'}), 401
        
        progress = badge_service.get_user_progress(username)
        return jsonify(progress), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500