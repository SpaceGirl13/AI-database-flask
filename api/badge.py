# api/badge.py - Flask Blueprint for Badge System
from flask import Blueprint, request, jsonify, g
from api.jwt_authorize import token_required
from model.user import User
from model.badge_t import Badge, UserBadge
from __init__ import db
from datetime import datetime

# Create Blueprint
badge_api = Blueprint('badge_api', __name__, url_prefix='/api/badges')


@badge_api.route('/definitions', methods=['GET'])
def get_badge_definitions():
    """Get all badge definitions"""
    try:
        badges = Badge.query.all()
        badge_list = [badge.read() for badge in badges]
        return jsonify({
            'success': True,
            'badges': {badge['id']: {k: v for k, v in badge.items() if k != 'id'} for badge in badge_list}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@badge_api.route('/my-badges', methods=['GET'])
@token_required()
def get_my_badges():
    """Get current user's badges"""
    current_user = g.current_user
    try:
        # Try transactional junction table first
        user_badges_objs = UserBadge.query.filter_by(user_id=current_user.id).all()
        user_badges = [ub.badge.read() for ub in user_badges_objs]
        return jsonify({
            'success': True,
            'badges': user_badges,
            'badge_count': len(user_badges)
        }), 200
    except Exception as e:
        # Fallback to JSON-backed badges on OperationalError or table-missing
        if 'no such table' in str(e).lower() or 'operationalerror' in str(e).lower():
            data = current_user.read_badges()
            return jsonify({
                'success': True,
                'badges': [{'id': b, 'name': b} for b in data['badges']],
                'badge_count': data['badge_count']
            }), 200
        return jsonify({'error': str(e)}), 500


@badge_api.route('/award', methods=['POST'])
@token_required()
def award_badge():
    """Award a badge to the current user"""
    current_user = g.current_user
    body = request.get_json()

    badge_id = body.get('badge_id')
    if not badge_id:
        return jsonify({'error': 'badge_id is required'}), 400

    # Get badge by badge_id (string identifier)
    badge = Badge.query.filter_by(_badge_id=badge_id).first()
    if not badge:
        return jsonify({'error': 'Invalid badge_id'}), 400

    # Try awarding via the junction table; fallback to JSON if table missing
    try:
        existing = UserBadge.query.filter_by(user_id=current_user.id, badge_id=badge.id).first()
        if existing:
            return jsonify({'success': True, 'message': 'Badge already earned', 'badge': badge.read(), 'new_badge': False}), 200

        user_badge = UserBadge(user_id=current_user.id, badge_id=badge.id)
        created = user_badge.create()
        if created:
            return jsonify({'success': True, 'message': f'Badge "{badge.name}" awarded!', 'badge': badge.read(), 'new_badge': True}), 200
        # fallback to JSON method if create() returned None
        added = current_user.add_badge(badge_id)
        if added:
            return jsonify({'success': True, 'message': f'Badge "{badge.name}" awarded (fallback)!', 'badge': badge.read(), 'new_badge': True}), 200
        return jsonify({'success': False, 'message': 'Failed to award badge'}), 500
    except Exception as e:
        # Fallback: likely OperationalError (no table). Use JSON-backed add_badge
        if 'no such table' in str(e).lower() or 'operationalerror' in str(e).lower():
            added = current_user.add_badge(badge_id)
            if added:
                return jsonify({'success': True, 'message': f'Badge "{badge.name}" awarded (fallback)!', 'badge': badge.read(), 'new_badge': True}), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to award badge (fallback)'}), 500
        return jsonify({'error': str(e)}), 500


@badge_api.route('/check-progress', methods=['GET'])
@token_required()
def check_progress():
    """Check user's progress towards all badges"""
    current_user = g.current_user
    try:
        all_badges = Badge.query.all()
        try:
            user_badge_objs = UserBadge.query.filter_by(user_id=current_user.id).all()
            earned_badge_ids = {ub.badge_id for ub in user_badge_objs}
        except Exception as e:
            # Fallback to JSON-backed badges
            if 'no such table' in str(e).lower() or 'operationalerror' in str(e).lower():
                earned_badge_ids = set()
                for bid in (current_user.badges or []):
                    b = Badge.query.filter_by(_badge_id=bid).first()
                    if b:
                        earned_badge_ids.add(b.id)
            else:
                raise

        progress = []
        for badge in all_badges:
            progress.append({
                'id': badge._badge_id,
                'name': badge.name,
                'description': badge.description,
                'requirement': badge.requirement,
                'earned': badge.id in earned_badge_ids
            })

        return jsonify({
            'success': True,
            'progress': progress,
            'total_badges': len(all_badges),
            'earned_badges': len(earned_badge_ids)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@badge_api.route('/user/<uid>', methods=['GET'])
@token_required()
def get_user_badges(uid):
    """Get badges for a specific user (Admin or self only)"""
    current_user = g.current_user
    try:
        if current_user.role != 'Admin' and current_user.uid != uid:
            return jsonify({'error': 'Permission denied'}), 403

        user = User.query.filter_by(_uid=uid).first()
        if not user:
            return jsonify({'error': f'User {uid} not found'}), 404

        try:
            user_badge_objs = UserBadge.query.filter_by(user_id=user.id).all()
            user_badges = [ub.badge.read() for ub in user_badge_objs]
        except Exception as e:
            if 'no such table' in str(e).lower() or 'operationalerror' in str(e).lower():
                data = user.read_badges()
                user_badges = [{'id': b, 'name': b} for b in data['badges']]
            else:
                raise

        return jsonify({
            'success': True,
            'uid': user.uid,
            'name': user.name,
            'badges': user_badges,
            'badge_count': len(user_badges)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@badge_api.route('/leaderboard', methods=['GET'])
def get_badge_leaderboard():
    """Get top users by badge count"""
    try:
        leaderboard = []
        try:
            badge_counts = db.session.query(
                UserBadge.user_id,
                db.func.count(UserBadge.badge_id).label('badge_count')
            ).group_by(UserBadge.user_id).all()

            for user_id, count in badge_counts:
                user = User.query.filter_by(id=user_id).first()
                if user and count > 0:
                    user_badge_objs = UserBadge.query.filter_by(user_id=user_id).all()
                    badge_ids = [ub.badge._badge_id for ub in user_badge_objs]
                    leaderboard.append({'uid': user.uid, 'name': user.name, 'badge_count': count, 'badges': badge_ids})
        except Exception as e:
            # Fallback: compute leaderboard from users' JSON-backed badges
            if 'no such table' in str(e).lower() or 'operationalerror' in str(e).lower():
                users = User.query.all()
                for user in users:
                    data = user.read_badges()
                    count = data['badge_count']
                    if count > 0:
                        leaderboard.append({'uid': user.uid, 'name': user.name, 'badge_count': count, 'badges': data['badges']})
            else:
                raise

        leaderboard.sort(key=lambda x: x['badge_count'], reverse=True)
        return jsonify({'success': True, 'leaderboard': leaderboard[:10]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_badge_info(badge_id):
    """Get complete badge information including image URL"""
    badge = Badge.query.filter_by(_badge_id=badge_id).first()
    if badge:
        return badge.read()
    return None