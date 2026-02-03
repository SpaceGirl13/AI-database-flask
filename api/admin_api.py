"""Admin API for managing database tables"""
from flask import Blueprint, jsonify, request
from __init__ import db
from model.survey_results import SurveyResponse, AIToolPreference, initSurveyResults
from model.questions import Question, initQuestions
from model.leaderboard import LeaderboardEntry, initLeaderboard
from model.submodule_feedback import SubmoduleFeedback, initSubmoduleFeedback
from model.feedback import Feedback, initFeedback
from model.badge_t import Badge, UserBadge, init_badges
from model.user import User

admin_api = Blueprint('admin_api', __name__, url_prefix='/api/admin')


# ========== Manual Seed Endpoint ==========

@admin_api.route('/seed-data', methods=['POST'])
def seed_data():
    """Manually seed the database with initial data"""
    results = {
        'survey': {'before': 0, 'after': 0, 'error': None},
        'leaderboard': {'before': 0, 'after': 0, 'error': None},
        'questions': {'before': 0, 'after': 0, 'error': None},
        'submodule_feedback': {'before': 0, 'after': 0, 'error': None}
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

    # Seed submodule feedback
    try:
        results['submodule_feedback']['before'] = SubmoduleFeedback.query.count()
        if results['submodule_feedback']['before'] == 0:
            initSubmoduleFeedback()
        results['submodule_feedback']['after'] = SubmoduleFeedback.query.count()
    except Exception as e:
        results['submodule_feedback']['error'] = str(e)

    # Seed general feedbacks
    results['feedbacks'] = {'before': 0, 'after': 0, 'error': None}
    try:
        results['feedbacks']['before'] = Feedback.query.count()
        if results['feedbacks']['before'] == 0:
            initFeedback()
        results['feedbacks']['after'] = Feedback.query.count()
    except Exception as e:
        results['feedbacks']['error'] = str(e)

    return jsonify(results)


@admin_api.route('/reset-tables', methods=['POST'])
def reset_tables():
    """Drop and recreate survey_responses, ai_tool_preferences, leaderboard, and submodule_feedback tables, then seed them"""
    results = {
        'dropped': [],
        'created': [],
        'seeded': {},
        'errors': []
    }

    try:
        # Drop the tables in correct order (ai_tool_preferences first due to foreign key)
        AIToolPreference.__table__.drop(db.engine, checkfirst=True)
        results['dropped'].append('ai_tool_preferences')

        SurveyResponse.__table__.drop(db.engine, checkfirst=True)
        results['dropped'].append('survey_responses')

        LeaderboardEntry.__table__.drop(db.engine, checkfirst=True)
        results['dropped'].append('leaderboard')

        SubmoduleFeedback.__table__.drop(db.engine, checkfirst=True)
        results['dropped'].append('submodule_feedback')

        Feedback.__table__.drop(db.engine, checkfirst=True)
        results['dropped'].append('feedbacks')

        # Recreate the tables
        SurveyResponse.__table__.create(db.engine, checkfirst=True)
        results['created'].append('survey_responses')

        AIToolPreference.__table__.create(db.engine, checkfirst=True)
        results['created'].append('ai_tool_preferences')

        LeaderboardEntry.__table__.create(db.engine, checkfirst=True)
        results['created'].append('leaderboard')

        SubmoduleFeedback.__table__.create(db.engine, checkfirst=True)
        results['created'].append('submodule_feedback')

        Feedback.__table__.create(db.engine, checkfirst=True)
        results['created'].append('feedbacks')

        # Seed the data
        try:
            initSurveyResults()
            results['seeded']['survey_responses'] = SurveyResponse.query.count()
            results['seeded']['ai_tool_preferences'] = AIToolPreference.query.count()
        except Exception as e:
            results['errors'].append(f"Survey seeding error: {str(e)}")

        try:
            initLeaderboard()
            results['seeded']['leaderboard'] = LeaderboardEntry.query.count()
        except Exception as e:
            results['errors'].append(f"Leaderboard seeding error: {str(e)}")

        try:
            initSubmoduleFeedback()
            results['seeded']['submodule_feedback'] = SubmoduleFeedback.query.count()
        except Exception as e:
            results['errors'].append(f"Submodule feedback seeding error: {str(e)}")

        try:
            initFeedback()
            results['seeded']['feedbacks'] = Feedback.query.count()
        except Exception as e:
            results['errors'].append(f"Feedbacks seeding error: {str(e)}")

    except Exception as e:
        results['errors'].append(str(e))

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

@admin_api.route('/leaderboard', methods=['POST'])
def create_leaderboard_entry():
    """Create a new leaderboard entry (transaction)"""
    from model.user import User

    data = request.get_json()

    # Require user_id for normalized schema
    user_id = data.get('user_id')
    uid = data.get('uid')  # Alternative: look up by uid

    if not user_id and uid:
        user = User.query.filter_by(_uid=uid).first()
        if user:
            user_id = user.id

    if not user_id:
        return jsonify({'error': 'user_id or valid uid is required'}), 400

    score = data.get('score', 0)
    correct_answers = data.get('correctAnswers', 0)

    entry = LeaderboardEntry(
        user_id=user_id,
        score=score,
        correct_answers=correct_answers
    )
    entry.create()
    return jsonify(entry.read()), 201

@admin_api.route('/leaderboard/<int:id>', methods=['PUT'])
def update_leaderboard_entry(id):
    """Update a leaderboard entry (transaction data)"""
    from model.user import User

    entry = LeaderboardEntry.query.get_or_404(id)
    data = request.get_json()

    # Allow updating user_id (normalized foreign key)
    if 'user_id' in data:
        entry.user_id = data['user_id']
    elif 'uid' in data:
        # Look up user by uid for convenience
        user = User.query.filter_by(_uid=data['uid']).first()
        if user:
            entry.user_id = user.id

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

# ========== Submodule Feedback ==========

@admin_api.route('/submodule-feedback', methods=['GET'])
def get_all_submodule_feedback():
    """Get all submodule feedback entries"""
    category = request.args.get('category')
    if category:
        entries = SubmoduleFeedback.get_by_category(category)
    else:
        entries = SubmoduleFeedback.get_all_feedback()
    return jsonify([entry.read() for entry in entries])

@admin_api.route('/submodule-feedback/stats', methods=['GET'])
def get_submodule_feedback_stats():
    """Get feedback statistics"""
    return jsonify({
        'total_count': SubmoduleFeedback.query.count(),
        'submodule2_count': len(SubmoduleFeedback.get_by_category('submodule2')),
        'submodule3_count': len(SubmoduleFeedback.get_by_category('submodule3')),
        'average_rating': SubmoduleFeedback.get_average_rating(),
        'submodule2_avg_rating': SubmoduleFeedback.get_average_rating('submodule2'),
        'submodule3_avg_rating': SubmoduleFeedback.get_average_rating('submodule3')
    })

@admin_api.route('/submodule-feedback/<int:id>', methods=['GET'])
def get_submodule_feedback(id):
    """Get a single feedback entry"""
    entry = SubmoduleFeedback.query.get_or_404(id)
    return jsonify(entry.read())

@admin_api.route('/submodule-feedback', methods=['POST'])
def create_submodule_feedback():
    """Create a new submodule feedback entry (transaction)"""
    from model.user import User

    data = request.get_json()

    # Require user_id for normalized schema
    user_id = data.get('user_id')
    uid = data.get('uid')  # Alternative: look up by uid

    if not user_id and uid:
        user = User.query.filter_by(_uid=uid).first()
        if user:
            user_id = user.id

    if not user_id:
        return jsonify({'error': 'user_id or valid uid is required'}), 400

    rating = data.get('rating', 3)
    category = data.get('category', 'submodule2')
    comments = data.get('comments')

    entry = SubmoduleFeedback(
        user_id=user_id,
        rating=rating,
        category=category,
        comments=comments
    )
    entry.create()
    return jsonify(entry.read()), 201

@admin_api.route('/submodule-feedback/<int:id>', methods=['PUT'])
def update_submodule_feedback(id):
    """Update a feedback entry (transaction data)"""
    from model.user import User

    entry = SubmoduleFeedback.query.get_or_404(id)
    data = request.get_json()

    # Allow updating user_id (normalized foreign key)
    if 'user_id' in data:
        entry.user_id = data['user_id']
    elif 'uid' in data:
        user = User.query.filter_by(_uid=data['uid']).first()
        if user:
            entry.user_id = user.id

    if 'rating' in data:
        entry.rating = data['rating']
    if 'category' in data:
        entry.category = data['category']
    if 'comments' in data:
        entry.comments = data['comments']

    db.session.commit()
    return jsonify(entry.read())

@admin_api.route('/submodule-feedback/<int:id>', methods=['DELETE'])
def delete_submodule_feedback(id):
    """Delete a feedback entry"""
    entry = SubmoduleFeedback.query.get_or_404(id)
    entry.delete()
    return jsonify({'message': 'Feedback entry deleted'})


# ========== Badges & User Badges Management ==========
@admin_api.route('/badges', methods=['GET'])
def get_badges():
    """Return all badge definitions"""
    try:
        badges = Badge.query.all()
        return jsonify([b.read() for b in badges])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api.route('/user-badges', methods=['GET'])
def get_user_badges():
    """Return user-badge mappings"""
    try:
        limit = request.args.get('limit', 100, type=int)
        ubs = UserBadge.query.limit(limit).all()
        results = []
        for ub in ubs:
            results.append({
                'user_id': ub.user_id,
                'uid': ub.user._uid if ub.user else None,
                'username': ub.user._name if ub.user else None,
                'badge_id': ub.badge._badge_id if ub.badge else None,
                'badge_name': ub.badge._name if ub.badge else None,
                'awarded_at': ub.awarded_at.isoformat() if ub.awarded_at else None
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api.route('/user-badges', methods=['POST'])
def create_user_badge():
    """Create a new user-badge mapping. Accepts JSON: {"uid": "alice", "badge_id": "delightful_data_scientist"} or user_id + badge_id"""
    try:
        data = request.get_json() or {}
        uid = data.get('uid')
        user_id = data.get('user_id')
        badge_key = data.get('badge_id')
        if not (badge_key and (uid or user_id)):
            return jsonify({'error': 'badge_id and (uid or user_id) required'}), 400

        user = None
        if user_id:
            user = User.query.get(user_id)
        else:
            user = User.query.filter_by(_uid=uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        badge = Badge.query.filter_by(_badge_id=badge_key).first()
        if not badge:
            return jsonify({'error': 'Badge not found'}), 404

        exists = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
        if exists:
            return jsonify({'success': True, 'message': 'Already exists'}), 200

        ub = UserBadge(user_id=user.id, badge_id=badge.id)
        created = ub.create()
        if created:
            return jsonify({'success': True, 'mapping': {'user_id': user.id, 'badge_id': badge._badge_id}}), 201
        return jsonify({'error': 'Failed to create mapping'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api.route('/user-badges', methods=['DELETE'])
def delete_user_badge():
    """Delete a user-badge mapping. Accepts JSON: {"uid": "alice", "badge_id": "delightful_data_scientist"} or user_id + badge_id"""
    try:
        data = request.get_json() or {}
        uid = data.get('uid')
        user_id = data.get('user_id')
        badge_key = data.get('badge_id')
        if not (badge_key and (uid or user_id)):
            return jsonify({'error': 'badge_id and (uid or user_id) required'}), 400

        user = None
        if user_id:
            user = User.query.get(user_id)
        else:
            user = User.query.filter_by(_uid=uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        badge = Badge.query.filter_by(_badge_id=badge_key).first()
        if not badge:
            return jsonify({'error': 'Badge not found'}), 404

        mapping = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
        if not mapping:
            return jsonify({'success': True, 'message': 'Mapping not found'}), 200

        mapping.delete()
        return jsonify({'success': True, 'message': 'Mapping deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
