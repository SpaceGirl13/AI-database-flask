# submodule3.py - Flask Blueprint for AI Prompt Challenge Game
from flask import Blueprint, request, jsonify, g
import json
import os
from datetime import datetime
from api.jwt_authorize import token_required
from model.user import User

# Create Blueprint
game_api = Blueprint('game_api', __name__)

# Data files
QUESTIONS_FILE = 'game_questions.json'
SCORES_FILE = 'game_scores.json'

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

def load_scores():
    """Load scores from database file"""
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return {'scores': []}

def save_scores(data):
    """Save scores to database file"""
    with open(SCORES_FILE, 'w') as f:
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
@token_required()
def save_score():
    """Save a player's score"""
    try:
        current_user = g.current_user
        score_data = request.json

        # Validate required fields
        required_fields = ['score', 'correctAnswers', 'timestamp']
        for field in required_fields:
            if field not in score_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Add user info
        score_data['playerName'] = current_user.name
        score_data['uid'] = current_user.uid

        # Load existing scores
        data = load_scores()

        # Add new score
        data['scores'].append(score_data)

        # Save back to file
        save_scores(data)

        # Check if user made leaderboard (top 10)
        sorted_scores = sorted(data['scores'], key=lambda x: (-x['score'], x['timestamp']))
        top_10_uids = [s.get('uid') for s in sorted_scores[:10]]
        
        badge_awarded = False
        if current_user.uid in top_10_uids:
            badge_awarded = current_user.add_badge('super_smart_genius')

        response_data = {
            'success': True,
            'message': 'Score saved successfully'
        }
        
        if badge_awarded:
            response_data['badge_awarded'] = {
                'id': 'super_smart_genius',
                'name': 'Super Smart Genius'
            }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_api.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top 10 scores"""
    try:
        data = load_scores()

        # Sort scores by score (descending), then by timestamp (ascending for ties)
        sorted_scores = sorted(
            data['scores'],
            key=lambda x: (-x['score'], x['timestamp'])
        )

        # Return top 10
        leaderboard = sorted_scores[:10]

        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_api.route('/complete', methods=['POST'])
@token_required()
def complete_submodule():
    """Mark submodule 3 as complete and award badge"""
    try:
        current_user = g.current_user
        badge_awarded = current_user.add_badge('prodigy_problem_solver')
        
        return jsonify({
            'success': True,
            'message': 'Submodule 3 completed!',
            'badge_awarded': badge_awarded,
            'badge': {
                'id': 'prodigy_problem_solver',
                'name': 'Prodigy Problem Solver'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500