from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from model.cs_prompt import CSPrompt
from model.user import User
from api.jwt_authorize import optional_token, token_required
from __init__ import app, db

cs_prompt_api = Blueprint('cs_prompt_api', __name__, url_prefix='/api/cs-prompts')
api = Api(cs_prompt_api)


class CSPromptAPI:
    """API endpoints for CS Prompt transactional data"""

    class _GetAll(Resource):
        """Get top 3 most recent CS prompts for the table display"""
        def get(self):
            try:
                # Get top 3 most recent prompts from database
                prompts = CSPrompt.get_recent(limit=3)

                if prompts:
                    return jsonify({
                        'success': True,
                        'prompts': [{
                            'prompt': p.prompt,
                            'type': p.prompt_type,
                            'username': p.username,
                            'score': p.score,
                            'created_at': p.created_at.isoformat() if p.created_at else None
                        } for p in prompts]
                    })

                # Return sample data if no prompts in database
                sample_prompts = [
                    {"prompt": "Write a Python function that calculates the factorial of a number using recursion.", "type": "Good", "username": "student1"},
                    {"prompt": "Create a JavaScript function to validate email addresses using regex.", "type": "Good", "username": "student2"},
                    {"prompt": "make code", "type": "Bad", "username": "student3"}
                ]

                return jsonify({
                    'success': True,
                    'prompts': sample_prompts
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

    class _GetByType(Resource):
        """Get prompts filtered by type (Good/Bad)"""
        def get(self, prompt_type):
            try:
                # Normalize type
                normalized_type = prompt_type.capitalize()

                prompts = CSPrompt.get_by_type(normalized_type, limit=10)

                return jsonify({
                    'success': True,
                    'prompts': [p.read() for p in prompts]
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

    class _Create(Resource):
        """Create a new CS prompt entry"""
        @optional_token()
        def post(self):
            try:
                data = request.get_json()
                prompt_text = data.get('prompt', '').strip()
                prompt_type = data.get('type', 'Custom')
                score = data.get('score')
                improved_version = data.get('improved_version')

                if not prompt_text:
                    return jsonify({'success': False, 'error': 'Prompt is required'}), 400

                # Get user_id if authenticated
                user_id = None
                if hasattr(g, 'current_user') and g.current_user:
                    user_id = g.current_user.id

                # Create the prompt entry
                cs_prompt = CSPrompt(
                    prompt=prompt_text,
                    prompt_type=prompt_type,
                    user_id=user_id,
                    score=score,
                    improved_version=improved_version
                )

                result = cs_prompt.create()

                if result:
                    return jsonify({
                        'success': True,
                        'message': 'Prompt saved successfully',
                        'prompt': result.read()
                    })
                else:
                    return jsonify({'success': False, 'error': 'Failed to save prompt'}), 500

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

    class _GetUserPrompts(Resource):
        """Get prompts for a specific user"""
        @token_required()
        def get(self):
            try:
                user_id = g.current_user.id if hasattr(g, 'current_user') and g.current_user else None

                if not user_id:
                    return jsonify({'success': False, 'error': 'User not authenticated'}), 401

                prompts = CSPrompt.get_by_user(user_id, limit=20)

                return jsonify({
                    'success': True,
                    'prompts': [p.read() for p in prompts]
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

    class _Delete(Resource):
        """Delete a CS prompt entry"""
        @token_required()
        def delete(self, prompt_id):
            try:
                prompt = CSPrompt.query.get(prompt_id)

                if not prompt:
                    return jsonify({'success': False, 'error': 'Prompt not found'}), 404

                # Check if user owns this prompt
                user_id = g.current_user.id if hasattr(g, 'current_user') and g.current_user else None
                if prompt.user_id != user_id:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 403

                prompt.delete()

                return jsonify({
                    'success': True,
                    'message': 'Prompt deleted successfully'
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500


# Register API resources
api.add_resource(CSPromptAPI._GetAll, '/')
api.add_resource(CSPromptAPI._GetByType, '/type/<string:prompt_type>')
api.add_resource(CSPromptAPI._Create, '/create')
api.add_resource(CSPromptAPI._GetUserPrompts, '/my-prompts')
api.add_resource(CSPromptAPI._Delete, '/delete/<int:prompt_id>')
