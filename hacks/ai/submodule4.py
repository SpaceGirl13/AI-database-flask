# app.py - Complete Flask Backend
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
LEADERBOARD_FILE = 'leaderboard_data.json'

def load_leaderboard():
    """Load leaderboard data from JSON file"""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    else:
        return {'scores': []}

def save_leaderboard(data):
    """Save leaderboard data to JSON file"""
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_top_10(scores):
    """Get top 10 scores sorted by score descending"""
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return sorted_scores[:10]

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top 10 leaderboard scores"""
    try:
        data = load_leaderboard()
        top_10 = get_top_10(data['scores'])
        
        # Add rank to each entry
        leaderboard_with_rank = []
        for index, entry in enumerate(top_10, start=1):
            leaderboard_with_rank.append({
                'rank': index,
                'name': entry['name'],
                'score': entry['score'],
                'timestamp': entry.get('timestamp', '')
            })
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_with_rank
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard', methods=['POST'])
def submit_score():
    """Submit a new score to the leaderboard"""
    try:
        score_data = request.json
        
        # Validate required fields
        if 'name' not in score_data or 'score' not in score_data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: name and score'
            }), 400
        
        # Validate score is a number
        try:
            score = int(score_data['score'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Score must be a number'
            }), 400
        
        # Validate name is not empty
        name = score_data['name'].strip()
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name cannot be empty'
            }), 400
        
        # Load current data
        data = load_leaderboard()
        
        # Create new entry
        new_entry = {
            'name': name,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to scores list
        data['scores'].append(new_entry)
        
        # Save updated data
        save_leaderboard(data)
        
        # Get updated top 10
        top_10 = get_top_10(data['scores'])
        leaderboard_with_rank = []
        for index, entry in enumerate(top_10, start=1):
            leaderboard_with_rank.append({
                'rank': index,
                'name': entry['name'],
                'score': entry['score'],
                'timestamp': entry.get('timestamp', '')
            })
        
        return jsonify({
            'success': True,
            'message': 'Score submitted successfully',
            'leaderboard': leaderboard_with_rank
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard/clear', methods=['POST'])
def clear_leaderboard():
    """Clear all leaderboard data (admin use only)"""
    try:
        data = {'scores': []}
        save_leaderboard(data)
        
        return jsonify({
            'success': True,
            'message': 'Leaderboard cleared successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard/stats', methods=['GET'])
def get_stats():
    """Get leaderboard statistics"""
    try:
        data = load_leaderboard()
        scores = [entry['score'] for entry in data['scores']]
        
        stats = {
            'total_entries': len(data['scores']),
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'average_score': sum(scores) / len(scores) if scores else 0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8001)  # Different port from survey app