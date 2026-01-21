# api/badge.py - Flask Blueprint for Badge System
from flask import Blueprint, request, jsonify, g
from api.jwt_authorize import token_required
from model.user import User
import json
import os
from datetime import datetime

# Create Blueprint
badge_api = Blueprint('badge_api', __name__, url_prefix='/api/badges')

# Badge definitions
BADGE_DEFINITIONS = {
    'delightful_data_scientist': {
        'name': 'Delightful Data Scientist',
        'description': 'Mastered foundational AI concepts and data literacy',
        'requirement': 'Complete Submodule 1',
        'type': 'submodule',
        'image_url': 'https://github.com/user-attachments/assets/d3d6f596-cae3-401d-9390-a3721aa7cfb3'
    },
    'perfect_prompt_engineer': {
        'name': 'Perfect Prompt Engineer',
        'description': 'Demonstrated expertise in crafting effective AI prompts',
        'requirement': 'Complete Submodule 2',
        'type': 'submodule',
        'image_url': 'https://github.com/user-attachments/assets/65a9a19a-4f0a-4e08-8a70-cd37c1e75b7d'
    },
    'prodigy_problem_solver': {
        'name': 'Prodigy Problem Solver',
        'description': 'Applied AI knowledge to solve real-world challenges',
        'requirement': 'Complete Submodule 3',
        'type': 'submodule',
        'image_url': 'https://github.com/user-attachments/assets/d85f749c-2380-4427-96af-20b462e65514'
    },
    'responsible_ai_master': {
        'name': 'Responsible AI Master',
        'description': 'Achieved comprehensive understanding of ethical AI practices',
        'requirement': 'Complete Entire Quest',
        'type': 'completion',
        'image_url': 'https://github.com/user-attachments/assets/93e2fc3f-4ab4-4eef-8369-6a4c3a18f660'
    },
    'super_smart_genius': {
        'name': 'Super Smart Genius',
        'description': 'Ranked among top performers in the platform',
        'requirement': 'Make the Leaderboard',
        'type': 'special',
        'image_url': 'https://github.com/user-attachments/assets/6a96f46c-b926-4c44-8926-1ffbba007a05'
    },
    'intelligent_instructor': {
        'name': 'Intelligent Instructor',
        'description': 'Crafted a high-quality, effective AI prompt',
        'requirement': 'Create a "Good" Prompt',
        'type': 'special',
        'image_url': 'https://github.com/user-attachments/assets/b1a7fc47-da59-4f14-a8d0-2b4c36df7cc5'
    },
    'sensational_surveyor': {
        'name': 'Sensational Surveyor',
        'description': 'Provided valuable feedback to improve the platform',
        'requirement': 'Submit the Survey',
        'type': 'special',  # ← ADDED COMMA HERE
        'image_url': 'https://github.com/user-attachments/assets/5aebe49f-d1e5-4340-bba0-7e3e5b3afae2'
    }
}

# Data file for tracking badge completions
DATA_FILE = 'instance/volumes/badge_data.json'

def load_badge_data():
    """Load badge tracking data"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'completions': {}}

def save_badge_data(data):
    """Save badge tracking data"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@badge_api.route('/definitions', methods=['GET'])
def get_badge_definitions():
    """Get all badge definitions"""
    try:
        return jsonify({
            'success': True,
            'badges': BADGE_DEFINITIONS
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@badge_api.route('/my-badges', methods=['GET'])
@token_required()
def get_my_badges():
    """Get current user's badges"""
    try:
        current_user = g.current_user
        
        # Get user's badges with full details
        user_badges = []
        for badge_id in (current_user.badges if current_user.badges else []):
            if badge_id in BADGE_DEFINITIONS:
                badge_info = BADGE_DEFINITIONS[badge_id].copy()
                badge_info['id'] = badge_id
                user_badges.append(badge_info)
        
        return jsonify({
            'success': True,
            'badges': user_badges,
            'badge_count': len(user_badges)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@badge_api.route('/award', methods=['POST'])
@token_required()
def award_badge():
    """Award a badge to the current user"""
    try:
        current_user = g.current_user
        body = request.get_json()
        
        badge_id = body.get('badge_id')
        if not badge_id:
            return jsonify({'error': 'badge_id is required'}), 400
        
        if badge_id not in BADGE_DEFINITIONS:
            return jsonify({'error': 'Invalid badge_id'}), 400
        
        # Add badge to user
        was_awarded = current_user.add_badge(badge_id)
        
        if was_awarded:
            # Track completion
            data = load_badge_data()
            if current_user.uid not in data['completions']:
                data['completions'][current_user.uid] = []
            
            data['completions'][current_user.uid].append({
                'badge_id': badge_id,
                'timestamp': datetime.now().isoformat()
            })
            save_badge_data(data)
            
            return jsonify({
                'success': True,
                'message': f'Badge "{BADGE_DEFINITIONS[badge_id]["name"]}" awarded!',
                'badge': BADGE_DEFINITIONS[badge_id],
                'new_badge': True
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': 'Badge already earned',
                'badge': BADGE_DEFINITIONS[badge_id],
                'new_badge': False
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@badge_api.route('/check-progress', methods=['GET'])
@token_required()
def check_progress():
    """Check user's progress towards all badges"""
    try:
        current_user = g.current_user
        user_badge_ids = current_user.badges if current_user.badges else []
        
        progress = []
        for badge_id, badge_info in BADGE_DEFINITIONS.items():
            progress.append({
                'id': badge_id,
                'name': badge_info['name'],
                'description': badge_info['description'],
                'requirement': badge_info['requirement'],
                'type': badge_info['type'],
                'earned': badge_id in user_badge_ids
            })
        
        return jsonify({
            'success': True,
            'progress': progress,
            'total_badges': len(BADGE_DEFINITIONS),
            'earned_badges': len(user_badge_ids)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@badge_api.route('/user/<uid>', methods=['GET'])
@token_required()
def get_user_badges(uid):
    """Get badges for a specific user (Admin or self only)"""
    try:
        current_user = g.current_user
        
        # Check permissions
        if current_user.role != 'Admin' and current_user.uid != uid:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Get target user
        user = User.query.filter_by(_uid=uid).first()
        if not user:
            return jsonify({'error': f'User {uid} not found'}), 404
        
        # Get user's badges with full details
        user_badges = []
        for badge_id in (user.badges if user.badges else []):
            if badge_id in BADGE_DEFINITIONS:
                badge_info = BADGE_DEFINITIONS[badge_id].copy()
                badge_info['id'] = badge_id
                user_badges.append(badge_info)
        
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
        users = User.query.all()
        
        leaderboard = []
        for user in users:
            badge_count = len(user.badges) if user.badges else 0
            if badge_count > 0:
                leaderboard.append({
                    'uid': user.uid,
                    'name': user.name,
                    'badge_count': badge_count,
                    'badges': user.badges if user.badges else []
                })
        
        # Sort by badge count descending
        leaderboard.sort(key=lambda x: x['badge_count'], reverse=True)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard[:10]  # Top 10
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def get_badge_info(badge_id):
    """Get complete badge information including image URL"""
    if badge_id in BADGE_DEFINITIONS:
        badge_info = BADGE_DEFINITIONS[badge_id].copy()
        badge_info['id'] = badge_id
        return badge_info
    return None