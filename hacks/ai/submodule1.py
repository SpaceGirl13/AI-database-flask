from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File to store survey data
DATA_FILE = 'survey_data.json'
# File to store leaderboard data
LEADERBOARD_FILE = 'leaderboard_data.json'

def load_data():
    """Load survey data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize empty data structure
        return {
            'english': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'math': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'science': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'cs': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'history': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'useAI': {'Yes': 0, 'No': 0},
            'frqs': []
        }

def save_data(data):
    """Save survey data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_leaderboard():
    """Load leaderboard data from file"""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    """Save leaderboard data to file"""
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_ranks(leaderboard):
    """Calculate ranks based on scores"""
    # Sort by score (descending), then by timestamp (ascending for ties)
    sorted_board = sorted(
        leaderboard, 
        key=lambda x: (-x['score'], x['timestamp'])
    )
    
    # Assign ranks
    for idx, entry in enumerate(sorted_board, 1):
        entry['rank'] = idx
    
    return sorted_board

# ============================================
# SURVEY ENDPOINTS (Existing)
# ============================================

@app.route('/api/survey', methods=['GET'])
def get_survey_data():
    """Get all survey data"""
    try:
        data = load_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    """Submit a new survey response"""
    try:
        # Get the form data from request
        form_data = request.json
        
        # Validate required fields
        required_fields = ['english', 'math', 'science', 'cs', 'history', 'useAI', 'frq']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Load existing data
        data = load_data()
        
        # Update counts for each subject
        data['english'][form_data['english']] += 1
        data['math'][form_data['math']] += 1
        data['science'][form_data['science']] += 1
        data['cs'][form_data['cs']] += 1
        data['history'][form_data['history']] += 1
        data['useAI'][form_data['useAI']] += 1
        
        # Add FRQ response with timestamp
        frq_entry = {
            'text': form_data['frq'],
            'timestamp': datetime.now().isoformat()
        }
        data['frqs'].insert(0, frq_entry)  # Add to beginning of list
        
        # Save updated data
        save_data(data)
        
        return jsonify({
            'message': 'Survey submitted successfully',
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey/recent-frqs', methods=['GET'])
def get_recent_frqs():
    """Get the 3 most recent FRQ responses"""
    try:
        data = load_data()
        recent_frqs = data['frqs'][:3]  # Get first 3 (most recent)
        return jsonify(recent_frqs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey/reset', methods=['POST'])
def reset_survey():
    """Reset all survey data (for testing purposes)"""
    try:
        initial_data = {
            'english': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'math': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'science': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'cs': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'history': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'useAI': {'Yes': 0, 'No': 0},
            'frqs': []
        }
        save_data(initial_data)
        return jsonify({'message': 'Survey data reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# LEADERBOARD ENDPOINTS (New)
# ============================================

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get current leaderboard"""
    try:
        leaderboard = load_leaderboard()
        leaderboard = calculate_ranks(leaderboard)
        
        # Get top N entries (default 10)
        limit = request.args.get('limit', 10, type=int)
        return jsonify({
            'success': True,
            'leaderboard': leaderboard[:limit],
            'total_players': len(leaderboard)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard/submit', methods=['POST'])
def submit_score():
    """Submit a new score to the leaderboard"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'username' not in data or 'score' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and score are required'
            }), 400
        
        username = data['username'].strip()
        score = data['score']
        
        # Validate username
        if not username or len(username) < 2 or len(username) > 20:
            return jsonify({
                'success': False,
                'error': 'Username must be between 2 and 20 characters'
            }), 400
        
        # Validate score
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            return jsonify({
                'success': False,
                'error': 'Score must be between 0 and 100'
            }), 400
        
        # Load current leaderboard
        leaderboard = load_leaderboard()
        
        # Check if user already exists
        existing_entry = next((entry for entry in leaderboard if entry['username'].lower() == username.lower()), None)
        
        if existing_entry:
            # Update score only if new score is higher
            if score > existing_entry['score']:
                existing_entry['score'] = score
                existing_entry['timestamp'] = datetime.now().isoformat()
                existing_entry['attempts'] = existing_entry.get('attempts', 1) + 1
                message = 'Score updated! New personal best!'
            else:
                existing_entry['attempts'] = existing_entry.get('attempts', 1) + 1
                message = 'Score submitted but did not beat your previous best'
        else:
            # Add new entry
            new_entry = {
                'username': username,
                'score': score,
                'timestamp': datetime.now().isoformat(),
                'attempts': 1
            }
            leaderboard.append(new_entry)
            message = 'Score submitted successfully!'
        
        # Recalculate ranks and save
        leaderboard = calculate_ranks(leaderboard)
        save_leaderboard(leaderboard)
        
        # Find user's current rank
        user_entry = next(entry for entry in leaderboard if entry['username'].lower() == username.lower())
        
        return jsonify({
            'success': True,
            'message': message,
            'user_data': {
                'username': user_entry['username'],
                'score': user_entry['score'],
                'rank': user_entry['rank'],
                'attempts': user_entry['attempts']
            },
            'leaderboard': leaderboard[:10]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard/user/<username>', methods=['GET'])
def get_user_stats(username):
    """Get statistics for a specific user"""
    try:
        leaderboard = load_leaderboard()
        leaderboard = calculate_ranks(leaderboard)
        
        user_entry = next((entry for entry in leaderboard if entry['username'].lower() == username.lower()), None)
        
        if not user_entry:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user_data': user_entry
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard/stats', methods=['GET'])
def get_leaderboard_stats():
    """Get overall leaderboard statistics"""
    try:
        leaderboard = load_leaderboard()
        
        if not leaderboard:
            return jsonify({
                'success': True,
                'stats': {
                    'total_players': 0,
                    'average_score': 0,
                    'highest_score': 0,
                    'total_attempts': 0
                }
            }), 200
        
        scores = [entry['score'] for entry in leaderboard]
        attempts = [entry.get('attempts', 1) for entry in leaderboard]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_players': len(leaderboard),
                'average_score': round(sum(scores) / len(scores), 2),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'total_attempts': sum(attempts)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard/reset', methods=['POST'])
def reset_leaderboard():
    """Reset the leaderboard (admin only - add authentication in production)"""
    try:
        # In production, add authentication/authorization here
        data = request.get_json()
        password = data.get('admin_password') if data else None
        
        # Simple password check (use proper auth in production)
        if password != 'admin123':
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 401
        
        save_leaderboard([])
        return jsonify({
            'success': True,
            'message': 'Leaderboard reset successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'survey': '/api/survey',
            'leaderboard': '/api/leaderboard'
        }
    }), 200

if __name__ == '__main__':
    # Create data files if they don't exist
    if not os.path.exists(LEADERBOARD_FILE):
        save_leaderboard([])
    
    app.run(debug=True, port=5000)