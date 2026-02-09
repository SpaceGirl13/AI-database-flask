# submodule3.py - Flask Blueprint for AI Prompt Challenge Game
from flask import Blueprint, request, jsonify, g
import json
import os
from datetime import datetime
from api.jwt_authorize import token_required, optional_token
from model.user import User
from model.leaderboard import LeaderboardEntry
from __init__ import db

# Create Blueprint
game_api = Blueprint('game_api', __name__)

# Data files
QUESTIONS_FILE = 'game_questions.json'

# Badge definitions (matching badge.py)
BADGE_DEFINITIONS = {
    'super_smart_genius': {
        'name': 'Super Smart Genius',
        'description': 'Ranked among top performers in the platform',
        'requirement': 'Make the Leaderboard',
        'type': 'special',
        'image_url': 'https://github.com/user-attachments/assets/6a96f46c-b926-4c44-8926-1ffbba007a05'
    },
    'prodigy_problem_solver': {
        'name': 'Prodigy Problem Solver',
        'description': 'Applied AI knowledge to solve real-world challenges',
        'requirement': 'Complete Submodule 3',
        'type': 'submodule',
        'image_url': 'https://github.com/user-attachments/assets/d85f749c-2380-4427-96af-20b462e65514'
    }
}

def get_badge_info(badge_id):
    """Get complete badge information including image URL"""
    if badge_id in BADGE_DEFINITIONS:
        badge_info = BADGE_DEFINITIONS[badge_id].copy()
        badge_info['id'] = badge_id
        return badge_info
    return None

def load_questions():
    """Load questions from database file"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize with default questions if file doesn't exist
        default_questions = {
            'questions': [
                # Multiple Choice - Prompt Engineering
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'subject': 'math',
                    'scenario': 'You need help solving this quadratic equation: 2x² + 5x - 3 = 0',
                    'options': [
                        {'text': 'Help with math homework', 'isCorrect': False, 'explanation': 'Way too vague - no specific problem or context.'},
                        {'text': 'Solve 2x² + 5x - 3 = 0 step-by-step using the quadratic formula. Show all work and explain each step.', 'isCorrect': True, 'explanation': 'Perfect! Specific equation, clear method, and requests explanation.'},
                        {'text': 'solve equation', 'isCorrect': False, 'explanation': 'Too vague - which equation? What method?'},
                        {'text': 'Solve 2x² + 5x - 3 = 0', 'isCorrect': False, 'explanation': 'Better, but missing request for step-by-step explanation and method.'}
                    ]
                },
                {
                    'id': 2,
                    'type': 'multiple_choice',
                    'subject': 'cs',
                    'scenario': 'You need to learn about Python loops for beginners',
                    'options': [
                        {'text': 'How do loops work in Python?', 'isCorrect': False, 'explanation': 'Too broad - needs specific types and examples.'},
                        {'text': 'python loops', 'isCorrect': False, 'explanation': 'Too vague - which type? What level?'},
                        {'text': 'Explain Python for loops and while loops to a beginner. Include: syntax, when to use each, and 2 simple examples for each. Use clear comments in code.', 'isCorrect': True, 'explanation': 'Perfect! Specific loop types, clear level, requests examples and comments.'},
                        {'text': 'Teach me about for loops', 'isCorrect': False, 'explanation': 'Missing language, level, and comparison with while loops.'}
                    ]
                },

                # Drag and Drop - Proper Prompt Order
                {
                    'id': 3,
                    'type': 'drag_drop',
                    'subject': 'science',
                    'scenario': 'Arrange these elements to create the BEST prompt for understanding photosynthesis:',
                    'items': [
                        {'id': 'a', 'text': 'Explain photosynthesis', 'order': 1},
                        {'id': 'b', 'text': 'in simple terms for a high school student', 'order': 2},
                        {'id': 'c', 'text': 'Include the chemical equation and main steps', 'order': 3},
                        {'id': 'd', 'text': 'Use everyday analogies to make it clear', 'order': 4}
                    ],
                    'correctOrder': ['a', 'b', 'c', 'd'],
                    'explanation': 'A good prompt starts with the main request, specifies the level, adds specific details needed, and requests helpful formats like analogies.'
                },
                {
                    'id': 4,
                    'type': 'drag_drop',
                    'subject': 'history',
                    'scenario': 'Arrange these to build an effective prompt for analyzing a historical document:',
                    'items': [
                        {'id': 'a', 'text': 'Analyze the Declaration of Independence', 'order': 1},
                        {'id': 'b', 'text': 'focusing on the grievances against King George III', 'order': 2},
                        {'id': 'c', 'text': 'Explain their historical significance', 'order': 3},
                        {'id': 'd', 'text': 'and how they justified revolution', 'order': 4}
                    ],
                    'correctOrder': ['a', 'b', 'c', 'd'],
                    'explanation': 'Effective historical analysis prompts specify the document, narrow the focus, and ask for significance and connections.'
                },

                # Ethics - Should vs. Shouldn't Use AI
                {
                    'id': 5,
                    'type': 'ethics',
                    'scenario': 'Your teacher assigned an essay where you must develop your own original argument about climate change.',
                    'question': 'How should you use AI for this assignment?',
                    'options': [
                        {'text': 'Ask AI to write the entire essay for you', 'isCorrect': False, 'category': 'plagiarism', 'explanation': 'This is plagiarism. The assignment requires YOUR original thinking.'},
                        {'text': 'Use AI to brainstorm different perspectives on climate change, then develop your own unique argument', 'isCorrect': True, 'category': 'appropriate', 'explanation': 'Perfect! Using AI for brainstorming and research while developing your own argument is ethical and educational.'},
                        {'text': 'Copy AI-generated paragraphs and change a few words', 'isCorrect': False, 'category': 'plagiarism', 'explanation': 'This is still plagiarism. Paraphrasing AI content without original thinking violates academic integrity.'},
                        {'text': 'Never use AI at all for any school assignment', 'isCorrect': False, 'category': 'too_strict', 'explanation': 'AI can be a valuable learning tool when used ethically for research, brainstorming, and understanding concepts.'}
                    ]
                },
                {
                    'id': 6,
                    'type': 'ethics',
                    'scenario': 'You are stuck on a difficult math problem and do not understand the concept.',
                    'question': 'What is the BEST way to use AI?',
                    'options': [
                        {'text': 'Copy the AI-generated answer without understanding it', 'isCorrect': False, 'category': 'shortcuts', 'explanation': 'You will not learn anything this way, and you will struggle on tests without AI.'},
                        {'text': 'Ask AI to explain the concept step-by-step, try the problem yourself, then check with AI', 'isCorrect': True, 'category': 'learning', 'explanation': 'Excellent! Using AI as a tutor to understand concepts and verify your work promotes real learning.'},
                        {'text': 'Have AI solve all your homework problems', 'isCorrect': False, 'category': 'dependency', 'explanation': 'This creates dependency and prevents you from learning. You need to practice to master concepts.'},
                        {'text': 'Avoid asking for help entirely', 'isCorrect': False, 'category': 'too_strict', 'explanation': 'Seeking help is important! AI can be a great tutor when used to understand, not just get answers.'}
                    ]
                },
                {
                    'id': 7,
                    'type': 'ethics',
                    'scenario': 'You are working on a group coding project and one teammate is not contributing.',
                    'question': 'How should your team use AI?',
                    'options': [
                        {'text': 'Use AI to write all the code so the lazy teammate does not matter', 'isCorrect': False, 'category': 'shortcuts', 'explanation': 'This defeats the purpose of learning to code and working as a team.'},
                        {'text': 'Use AI to explain concepts to the struggling teammate, then everyone writes their own code', 'isCorrect': True, 'category': 'collaboration', 'explanation': 'Perfect! AI can help teach and level up team members while everyone still contributes their own work.'},
                        {'text': 'Have AI generate different parts of the code and each person claims one', 'isCorrect': False, 'category': 'plagiarism', 'explanation': 'This is academic dishonesty. The project should showcase what YOU can do.'},
                        {'text': 'Do not use AI at all to make it fair', 'isCorrect': False, 'category': 'too_strict', 'explanation': 'AI can be a valuable learning resource. The key is using it to learn, not to replace learning.'}
                    ]
                },

                # More Multiple Choice
                {
                    'id': 8,
                    'type': 'multiple_choice',
                    'subject': 'science',
                    'scenario': 'You need to compare mitosis and meiosis for your biology essay',
                    'options': [
                        {'text': 'mitosis vs meiosis', 'isCorrect': False, 'explanation': 'Too vague - needs format and specific aspects.'},
                        {'text': 'Explain the difference between mitosis and meiosis', 'isCorrect': False, 'explanation': 'Better, but missing specific comparison points and format.'},
                        {'text': 'Create a comparison table of mitosis and meiosis. Include: number of divisions, daughter cells, genetic variation, and where each occurs. Add 2-3 sentences explaining why these differences matter.', 'isCorrect': True, 'explanation': 'Perfect! Specific format (table), clear comparison points, and asks for significance.'},
                        {'text': 'Compare cell division', 'isCorrect': False, 'explanation': 'Too broad - which types? What aspects?'}
                    ]
                },
                {
                    'id': 9,
                    'type': 'multiple_choice',
                    'subject': 'history',
                    'scenario': 'You need to write an essay on the causes of World War I',
                    'options': [
                        {'text': 'Why did World War I start?', 'isCorrect': False, 'explanation': 'Too broad - needs structure and depth.'},
                        {'text': 'List and explain the 4 main causes of World War I (MAIN: Militarism, Alliances, Imperialism, Nationalism). For each cause, provide 2-3 specific examples and explain how they led to war.', 'isCorrect': True, 'explanation': 'Perfect! Specific framework (MAIN), requests details and causation.'},
                        {'text': 'world war 1 causes', 'isCorrect': False, 'explanation': 'Too vague - needs depth and structure.'},
                        {'text': 'Explain what caused WW1', 'isCorrect': False, 'explanation': 'Better, but missing specific framework and example requests.'}
                    ]
                },
                {
                    'id': 10,
                    'type': 'ethics',
                    'scenario': 'You have a final exam tomorrow and have not studied. You have access to AI during the exam.',
                    'question': 'What should you do?',
                    'options': [
                        {'text': 'Use AI to answer all the exam questions', 'isCorrect': False, 'category': 'cheating', 'explanation': 'This is cheating and violates academic integrity. Exams test YOUR knowledge.'},
                        {'text': 'Do not use AI during the exam, but use it tonight to help understand key concepts', 'isCorrect': True, 'category': 'ethical', 'explanation': 'Great choice! Using AI to study is ethical, but using it during an exam is cheating.'},
                        {'text': 'Use AI for just the hard questions you do not know', 'isCorrect': False, 'category': 'cheating', 'explanation': 'This is still cheating. Any unauthorized assistance during an exam violates academic integrity.'},
                        {'text': 'Tell the teacher you want to reschedule because you did not study', 'isCorrect': False, 'category': 'avoidance', 'explanation': 'Better than cheating, but you should have studied. Use AI tonight to prepare as much as possible.'}
                    ]
                }
            ]
        }
        save_questions(default_questions)
        return default_questions

def save_questions(data):
    """Save questions to database file"""
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@game_api.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions for the game"""
    try:
        questions_data = load_questions()
        return jsonify({
            'success': True,
            'questions': questions_data['questions']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_api.route('/scores', methods=['POST'])
@optional_token()
def save_score():
    """Save a player's score to the database"""
    try:
        score_data = request.json

        # Validate required fields
        required_fields = ['score', 'correctAnswers']
        for field in required_fields:
            if field not in score_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get user_id if logged in
        user_id = None
        if hasattr(g, 'current_user') and g.current_user:
            user_id = g.current_user.id
        else:
            # For anonymous users, try to find or create a guest user
            # Or return error requiring login
            return jsonify({'error': 'Login required to save scores'}), 401

        # Create new leaderboard entry with user_id (foreign key)
        entry = LeaderboardEntry(
            user_id=user_id,
            score=score_data['score'],
            correct_answers=score_data['correctAnswers']
        )
        entry.create()

        # Check if user made leaderboard (top 10)
        top_entries = LeaderboardEntry.get_top_scores(10)
        top_10_uids = [e.uid for e in top_entries]

        was_newly_awarded = False
        badge_info = None
        if hasattr(g, 'current_user') and g.current_user and g.current_user.uid in top_10_uids:
            badge_id = 'super_smart_genius'
            was_newly_awarded = g.current_user.add_badge(badge_id)
            if was_newly_awarded:
                badge_info = get_badge_info(badge_id)

        response_data = {
            'success': True,
            'message': 'Score saved successfully',
            'entry': entry.read(),
            'badge_awarded': was_newly_awarded
        }

        if badge_info:
            response_data['badge'] = badge_info

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_api.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top 10 scores from database"""
    try:
        top_entries = LeaderboardEntry.get_top_scores(10)

        if top_entries:
            leaderboard = [entry.read() for entry in top_entries]
        else:
            # Return sample data if no entries exist
            leaderboard = [
                {"id": 1, "playerName": "PrompMaster", "score": 100, "correctAnswers": 10},
                {"id": 2, "playerName": "AIExpert", "score": 95, "correctAnswers": 9},
                {"id": 3, "playerName": "CodeWizard", "score": 90, "correctAnswers": 9},
                {"id": 4, "playerName": "TechGenius", "score": 85, "correctAnswers": 8},
                {"id": 5, "playerName": "DataNinja", "score": 80, "correctAnswers": 8},
            ]

        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@game_api.route('/complete', methods=['POST'])
@token_required()
def complete_submodule():
    """Mark submodule 3 as complete and award badge"""
    try:
        current_user = g.current_user
        badge_id = 'prodigy_problem_solver'
        was_newly_awarded = current_user.add_badge(badge_id)

        response_data = {
            'success': True,
            'message': 'Submodule 3 completed!',
            'badge_awarded': was_newly_awarded
        }

        if was_newly_awarded:
            badge_info = get_badge_info(badge_id)
            if badge_info:
                response_data['badge'] = badge_info

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
