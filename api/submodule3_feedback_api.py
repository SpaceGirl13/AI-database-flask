# submodule3_feedback_api.py - Flask Blueprint for Submodule Feedback (supports both submodule 2 and 3)
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from api.jwt_authorize import optional_token
from model.submodule_feedback import SubmoduleFeedback
from __init__ import db

# Create Blueprint
submodule3_feedback_api = Blueprint('submodule3_feedback_api', __name__)


@submodule3_feedback_api.route('/feedback', methods=['POST'])
@optional_token()
def submit_feedback():
    """Submit feedback for submodule 2 or 3"""
    try:
        feedback_data = request.json

        # Validate required fields
        required_fields = ['rating', 'category']
        for field in required_fields:
            if field not in feedback_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get username from token or request data
        if hasattr(g, 'current_user') and g.current_user:
            username = g.current_user.uid
        else:
            username = feedback_data.get('playerName', 'anonymous')

        # Validate rating is 1-5
        rating = int(feedback_data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # Validate category
        category = feedback_data['category']
        if category not in ['submodule2', 'submodule3']:
            return jsonify({'error': 'Category must be submodule2 or submodule3'}), 400

        # Create feedback entry
        feedback = SubmoduleFeedback(
            username=username,
            rating=rating,
            category=category,
            comments=feedback_data.get('comments', feedback_data.get('additionalComments', ''))
        )
        feedback.create()

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback.read()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@submodule3_feedback_api.route('/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """Get the most recent feedback and stats"""
    try:
        category = request.args.get('category')

        if category:
            entries = SubmoduleFeedback.get_by_category(category)
        else:
            entries = SubmoduleFeedback.get_all_feedback()

        if not entries:
            return jsonify({
                'success': True,
                'feedback': None,
                'averageRating': 0,
                'totalResponses': 0
            }), 200

        # Get most recent feedback
        recent = entries[0].read() if entries else None

        # Calculate average rating
        average_rating = SubmoduleFeedback.get_average_rating(category)

        return jsonify({
            'success': True,
            'feedback': recent,
            'averageRating': average_rating,
            'totalResponses': len(entries)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@submodule3_feedback_api.route('/feedback/all', methods=['GET'])
def get_all_feedback():
    """Get all feedback entries"""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', 50, type=int)

        if category:
            entries = SubmoduleFeedback.get_by_category(category)[:limit]
        else:
            entries = SubmoduleFeedback.get_all_feedback()[:limit]

        return jsonify({
            'success': True,
            'feedback': [entry.read() for entry in entries],
            'totalResponses': len(entries)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
