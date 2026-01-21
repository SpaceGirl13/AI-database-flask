"""Admin API for managing database tables"""
from flask import Blueprint, jsonify, request
from __init__ import db
from model.survey_results import SurveyUser, SurveyResponse, AIToolPreference
from model.questions import Question

admin_api = Blueprint('admin_api', __name__, url_prefix='/api/admin')

# ========== Survey Users ==========

@admin_api.route('/survey-users', methods=['GET'])
def get_survey_users():
    """Get all survey users"""
    users = SurveyUser.query.all()
    return jsonify([user.read() for user in users])

@admin_api.route('/survey-users/<int:id>', methods=['GET'])
def get_survey_user(id):
    """Get a single survey user"""
    user = SurveyUser.query.get_or_404(id)
    return jsonify(user.read())

@admin_api.route('/survey-users/<int:id>', methods=['PUT'])
def update_survey_user(id):
    """Update a survey user"""
    user = SurveyUser.query.get_or_404(id)
    data = request.get_json()

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify(user.read())

@admin_api.route('/survey-users/<int:id>', methods=['DELETE'])
def delete_survey_user(id):
    """Delete a survey user"""
    user = SurveyUser.query.get_or_404(id)
    user.delete()
    return jsonify({'message': 'Survey user deleted'})

# ========== Survey Responses ==========

@admin_api.route('/survey-responses', methods=['GET'])
def get_survey_responses():
    """Get all survey responses"""
    responses = SurveyResponse.query.all()
    return jsonify([resp.read() for resp in responses])

@admin_api.route('/survey-responses/<int:id>', methods=['GET'])
def get_survey_response(id):
    """Get a single survey response"""
    response = SurveyResponse.query.get_or_404(id)
    return jsonify(response.read())

@admin_api.route('/survey-responses/<int:id>', methods=['PUT'])
def update_survey_response(id):
    """Update a survey response"""
    response = SurveyResponse.query.get_or_404(id)
    data = request.get_json()

    if 'uses_ai_schoolwork' in data:
        response.uses_ai_schoolwork = data['uses_ai_schoolwork']
    if 'policy_perspective' in data:
        response.policy_perspective = data['policy_perspective']
    if 'badge_awarded' in data:
        response.badge_awarded = data['badge_awarded']

    db.session.commit()
    return jsonify(response.read())

@admin_api.route('/survey-responses/<int:id>', methods=['DELETE'])
def delete_survey_response(id):
    """Delete a survey response"""
    response = SurveyResponse.query.get_or_404(id)
    response.delete()
    return jsonify({'message': 'Survey response deleted'})

# ========== AI Tool Preferences ==========

@admin_api.route('/ai-preferences', methods=['GET'])
def get_ai_preferences():
    """Get all AI tool preferences"""
    prefs = AIToolPreference.query.all()
    return jsonify([pref.read() for pref in prefs])

@admin_api.route('/ai-preferences/<int:id>', methods=['GET'])
def get_ai_preference(id):
    """Get a single AI tool preference"""
    pref = AIToolPreference.query.get_or_404(id)
    return jsonify(pref.read())

@admin_api.route('/ai-preferences/<int:id>', methods=['PUT'])
def update_ai_preference(id):
    """Update an AI tool preference"""
    pref = AIToolPreference.query.get_or_404(id)
    data = request.get_json()

    if 'subject' in data:
        pref.subject = data['subject']
    if 'ai_tool' in data:
        pref.ai_tool = data['ai_tool']

    db.session.commit()
    return jsonify(pref.read())

@admin_api.route('/ai-preferences/<int:id>', methods=['DELETE'])
def delete_ai_preference(id):
    """Delete an AI tool preference"""
    pref = AIToolPreference.query.get_or_404(id)
    pref.delete()
    return jsonify({'message': 'AI preference deleted'})

# ========== Questions ==========

@admin_api.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions"""
    questions = Question.query.all()
    return jsonify([q.read() for q in questions])

@admin_api.route('/questions/<int:id>', methods=['GET'])
def get_question(id):
    """Get a single question"""
    question = Question.query.get_or_404(id)
    return jsonify(question.read())

@admin_api.route('/questions/<int:id>', methods=['PUT'])
def update_question(id):
    """Update a question"""
    question = Question.query.get_or_404(id)
    data = request.get_json()

    if 'subject' in data:
        question._subject = data['subject']
    if 'category' in data:
        question._category = data['category']
    if 'question' in data:
        question._question = data['question']
    if 'answer' in data:
        question._answer = data['answer']
    if 'prompt_template' in data:
        question._prompt_template = data['prompt_template']

    db.session.commit()
    return jsonify(question.read())

@admin_api.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    """Delete a question"""
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted'})
