# submodule1.py - Flask Blueprint for AI Usage Survey
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from model.user import User
from model.survey_results import SurveyUser, SurveyResponse, AIToolPreference
from api.jwt_authorize import optional_token
from __init__ import db
from sqlalchemy import func

# Create Blueprint
survey_api = Blueprint('survey_api', __name__)


def get_aggregated_data():
    """Query database and aggregate survey results for display"""
    ai_tools = ['ChatGPT', 'Claude', 'Gemini', 'Copilot']

    data = {
        'english': {tool: 0 for tool in ai_tools},
        'math': {tool: 0 for tool in ai_tools},
        'science': {tool: 0 for tool in ai_tools},
        'cs': {tool: 0 for tool in ai_tools},
        'history': {tool: 0 for tool in ai_tools},
        'useAI': {'Yes': 0, 'No': 0},
        'frqs': []
    }

    # Count AI tool preferences by subject
    preferences = db.session.query(
        AIToolPreference._subject,
        AIToolPreference._ai_tool,
        func.count(AIToolPreference.id)
    ).group_by(AIToolPreference._subject, AIToolPreference._ai_tool).all()

    for subject, ai_tool, count in preferences:
        if subject in data and ai_tool in data[subject]:
            data[subject][ai_tool] = count

    # Count useAI responses
    use_ai_counts = db.session.query(
        SurveyResponse._uses_ai_schoolwork,
        func.count(SurveyResponse.id)
    ).group_by(SurveyResponse._uses_ai_schoolwork).all()

    for use_ai, count in use_ai_counts:
        if use_ai in data['useAI']:
            data['useAI'][use_ai] = count

    # Get recent FRQs (policy perspectives) with user info
    recent_responses = SurveyResponse.query.filter(
        SurveyResponse._policy_perspective.isnot(None),
        SurveyResponse._policy_perspective != ''
    ).order_by(SurveyResponse._completed_at.desc()).limit(20).all()

    for response in recent_responses:
        # Get the username for this response
        survey_user = SurveyUser.query.get(response.user_id)
        username = survey_user._username if survey_user else 'anonymous'

        data['frqs'].append({
            'text': response._policy_perspective,
            'timestamp': response._completed_at.isoformat() if response._completed_at else datetime.now().isoformat(),
            'user_id': username
        })

    return data


@survey_api.route('/survey', methods=['GET'])
def get_survey_data():
    """Get aggregated survey data from database"""
    try:
        data = get_aggregated_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@survey_api.route('/survey', methods=['POST'])
@optional_token()
def submit_survey():
    """Submit a new survey response to the database"""
    try:
        form_data = request.json

        required_fields = ['english', 'math', 'science', 'cs', 'history', 'useAI', 'frq']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get or create user
        username = 'anonymous'
        if hasattr(g, 'current_user') and g.current_user:
            username = g.current_user.uid
        else:
            username = f'anonymous_{datetime.now().strftime("%Y%m%d%H%M%S%f")}'

        # Check if user exists, create if not
        survey_user = SurveyUser.query.filter_by(_username=username).first()
        if not survey_user:
            survey_user = SurveyUser(username=username)
            db.session.add(survey_user)
            db.session.commit()

        # Create survey response
        response = SurveyResponse(
            user_id=survey_user.id,
            uses_ai_schoolwork=form_data['useAI'],
            policy_perspective=form_data['frq'],
            badge_awarded=False
        )
        db.session.add(response)
        db.session.commit()

        # Create AI tool preferences for each subject
        subjects = ['english', 'math', 'science', 'cs', 'history']
        for subject in subjects:
            preference = AIToolPreference(
                response_id=response.id,
                subject=subject,
                ai_tool=form_data[subject]
            )
            db.session.add(preference)

        db.session.commit()

        # Award badge if user is logged in
        was_newly_awarded = False
        if hasattr(g, 'current_user') and g.current_user:
            was_newly_awarded = g.current_user.add_badge('sensational_surveyor')
            response.badge_awarded = was_newly_awarded
            db.session.commit()

        # Get updated aggregated data
        data = get_aggregated_data()

        response_data = {
            'message': 'Survey submitted successfully',
            'data': data,
            'badge_awarded': was_newly_awarded  # Always include boolean
        }

        if was_newly_awarded:  # Only include badge details if newly awarded
            response_data['badge'] = {
                'id': 'sensational_surveyor',
                'name': 'Sensational Surveyor'
            }

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
