"""Admin API for managing database tables"""
from flask import Blueprint, jsonify, request
from __init__ import db
from model.survey_results import SurveyResponse, AIToolPreference, initSurveyResults
from model.questions import Question, initQuestions
from model.leaderboard import LeaderboardEntry, initLeaderboard

admin_api = Blueprint('admin_api', __name__, url_prefix='/api/admin')


# ========== Manual Seed Endpoint ==========

@admin_api.route('/seed-data', methods=['POST'])
def seed_data():
    """Manually seed the database with initial data"""
    results = {
        'survey': {'before': 0, 'after': 0, 'error': None},
        'leaderboard': {'before': 0, 'after': 0, 'error': None},
        'questions': {'before': 0, 'after': 0, 'error': None}
    }

    # Seed survey responses
    try:
        results['survey']['before'] = SurveyResponse.query.count()
        if results['survey']['before'] == 0:
            initSurveyResults()
        results['survey']['after'] = SurveyResponse.query.count()
    except Exception as e:
        results['survey']['error'] = str(e)

    # Seed leaderboard
    try:
        results['leaderboard']['before'] = LeaderboardEntry.query.count()
        if results['leaderboard']['before'] == 0:
            initLeaderboard()
        results['leaderboard']['after'] = LeaderboardEntry.query.count()
    except Exception as e:
        results['leaderboard']['error'] = str(e)

    # Seed questions
    try:
        results['questions']['before'] = Question.query.count()
        if results['questions']['before'] == 0:
            initQuestions()
        results['questions']['after'] = Question.query.count()
    except Exception as e:
        results['questions']['error'] = str(e)

    return jsonify(results)

# ========== Survey Responses (with Username included) ==========

@admin_api.route('/survey-responses-with-users', methods=['GET'])
def get_survey_responses_with_users():
    """Get survey responses (username is now in the table), limited to 100 rows"""
    limit = request.args.get('limit', 100, type=int)
    responses = SurveyResponse.query.limit(limit).all()
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

    if 'username' in data:
        response.username = data['username']
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

# ========== AI Tool Preferences (Grouped by User) ==========

@admin_api.route('/ai-preferences-grouped', methods=['GET'])
def get_ai_preferences_grouped():
    """Get AI preferences grouped by user, showing all subjects in one row"""
    limit = request.args.get('limit', 100, type=int)

    # Get responses (limited)
    responses = SurveyResponse.query.limit(limit).all()

    result = []
    for resp in responses:
        # Get all preferences for this response
        prefs = AIToolPreference.query.filter_by(response_id=resp.id).all()

        # Format preferences as "Math - ChatGPT, English - Claude, etc."
        pref_strings = []
        for pref in prefs:
            subject = pref.subject.capitalize()
            pref_strings.append(f"{subject} - {pref.ai_tool}")

        preferences_str = ', '.join(pref_strings) if pref_strings else 'No preferences'

        result.append({
            'user_id': resp.user_id,
            'response_id': resp.id,
            'username': resp.username,
            'preferences': preferences_str
        })

    return jsonify(result)

@admin_api.route('/ai-preferences-by-user/<int:user_id>', methods=['GET'])
def get_ai_preferences_by_user(user_id):
    """Get all AI preferences for a specific user"""
    # Find the response for this user
    response = SurveyResponse.query.filter_by(user_id=user_id).first()
    if not response:
        return jsonify([])

    prefs = AIToolPreference.query.filter_by(response_id=response.id).all()
    return jsonify([pref.read() for pref in prefs])

@admin_api.route('/ai-preferences-by-user/<int:user_id>', methods=['PUT'])
def update_ai_preferences_by_user(user_id):
    """Update AI preferences for a specific user"""
    data = request.get_json()

    # Find the response for this user
    response = SurveyResponse.query.filter_by(user_id=user_id).first()
    if not response:
        return jsonify({'error': 'User response not found'}), 404

    # Update each subject preference
    subjects = ['math', 'english', 'science', 'cs', 'history']
    for subject in subjects:
        if subject in data and data[subject]:
            # Find existing preference or create new one
            pref = AIToolPreference.query.filter_by(
                response_id=response.id,
                _subject=subject
            ).first()

            if pref:
                pref.ai_tool = data[subject]
            else:
                # Create new preference
                new_pref = AIToolPreference(
                    response_id=response.id,
                    subject=subject,
                    ai_tool=data[subject]
                )
                db.session.add(new_pref)

    db.session.commit()
    return jsonify({'message': 'Preferences updated'})

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

# ========== Leaderboard ==========

@admin_api.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get all leaderboard entries"""
    entries = LeaderboardEntry.get_all_scores()
    return jsonify([entry.read() for entry in entries])

@admin_api.route('/leaderboard/<int:id>', methods=['GET'])
def get_leaderboard_entry(id):
    """Get a single leaderboard entry"""
    entry = LeaderboardEntry.query.get_or_404(id)
    return jsonify(entry.read())

@admin_api.route('/leaderboard/<int:id>', methods=['PUT'])
def update_leaderboard_entry(id):
    """Update a leaderboard entry"""
    entry = LeaderboardEntry.query.get_or_404(id)
    data = request.get_json()

    if 'uid' in data:
        entry.uid = data['uid']
    if 'playerName' in data:
        entry.player_name = data['playerName']
    if 'score' in data:
        entry.score = data['score']
    if 'correctAnswers' in data:
        entry.correct_answers = data['correctAnswers']

    db.session.commit()
    return jsonify(entry.read())

@admin_api.route('/leaderboard/<int:id>', methods=['DELETE'])
def delete_leaderboard_entry(id):
    """Delete a leaderboard entry"""
    entry = LeaderboardEntry.query.get_or_404(id)
    entry.delete()
    return jsonify({'message': 'Leaderboard entry deleted'})
