
"""
Gemini API for handling requests to the Gemini language model.
Supports text analysis, citation checking, and other AI-powered features.

Example frontend JavaScript code for reference:
const API_KEY = "your-api-key-here";
const ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}`;
fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        contents: [{
            parts: [{ text: `Please look at this text for correct academic citations, and recommend APA references for each area of concern: ${text}` }]
        }]
    })
});
"""
from __init__ import app
from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource
import requests
import re
from api.jwt_authorize import token_required

gemini_api = Blueprint('gemini_api', __name__, url_prefix='/api')
api = Api(gemini_api)

def markdown_to_plain_text(markdown_text):
    """
    Convert markdown formatted text to plain text by removing markdown syntax.
    Preserves code blocks by extracting their content.

    Args:
        markdown_text: Text with markdown formatting

    Returns:
        Plain text without markdown formatting
    """
    text = markdown_text

    # Extract code from code blocks (preserve code, just remove the markdown syntax)
    # Match triple backtick code blocks and extract the code content
    def replace_code_block(match):
        # Extract everything after the language identifier and before the closing ```
        code_content = match.group(1)
        return code_content

    text = re.sub(r'```(?:python|javascript|java|cpp|c|ruby|go|rust|swift|kotlin|php|sql|html|css|json|xml|yaml)?\n?([\s\S]*?)```', replace_code_block, text)

    # Remove inline code backticks but keep the content
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove headers (# ## ### etc)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bold/italic (**text** or __text__ or *text* or _text_)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)

    # Remove links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)

    # Remove horizontal rules (--- or ***)
    text = re.sub(r'^[\-\*]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Remove blockquotes (> )
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # Remove list markers (- or * or 1. )
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove strikethrough (~~text~~)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)

    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

class GeminiAPI:
    class _Ask(Resource):
        """
        Gemini API Resource to handle requests to the Gemini language model.
        Supports various AI-powered text analysis tasks.
        """
        # @token_required()  # Temporarily disabled for testing
        def post(self):
            """
            Send a request to the Gemini API.
            
            Expected JSON body:
            {
                "text": "Text to analyze",
                "prompt": "Optional custom prompt" (defaults to citation analysis)
            }
            
            Returns:
                JSON response from Gemini API or error message
            """
            # current_user = g.current_user  # Removed - not needed without token_required
            body = request.get_json()

            # Validate request body
            if not body:
                return {'message': 'Request body is required'}, 400

            text = body.get('text', '')
            if not text:
                return {'message': 'Text field is required'}, 400

            # Check if markdown conversion should be applied (default: True)
            convert_markdown = body.get('convert_markdown', True)
            
            # Get configuration
            api_key = app.config.get('GEMINI_API_KEY')
            server = app.config.get('GEMINI_SERVER')
            
            if not api_key:
                return {'message': 'Gemini API key not configured'}, 500
            
            if not server:
                return {'message': 'Gemini server not configured'}, 500
            
            # Build the endpoint URL
            endpoint = f"{server}?key={api_key}"
            
            # Default prompt for citation analysis, can be overridden
            default_prompt = f"Please look at this text for correct academic citations, and recommend APA references for each area of concern"
            prompt = body.get('prompt', default_prompt)
            
            # Prepare the request payload for Gemini API
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{prompt}: {text}"
                    }]
                }]
            }
            
            # Log the request for auditing purposes
            user_id = g.current_user.uid if hasattr(g, 'current_user') and g.current_user else 'anonymous'
            current_app.logger.info(f"User {user_id} made a Gemini API request")
            
            try:
                # Log the request details for debugging
                current_app.logger.info(f"Making request to Gemini API: {endpoint}")
                current_app.logger.debug(f"Payload: {payload}")
                
                # Make request to Gemini API
                response = requests.post(
                    endpoint,
                    headers={'Content-Type': 'application/json'},
                    json=payload,
                    timeout=90  # 90 second timeout
                )
                
                # Check if the request was successful
                if response.status_code != 200:
                    error_details = {
                        'status_code': response.status_code,
                        'response_text': response.text,
                        'endpoint': endpoint,
                        'headers': dict(response.headers)
                    }
                    current_app.logger.error(f"Gemini API error: {error_details}")
                    
                    # Handle specific error codes
                    if response.status_code == 503:
                        return {
                            'message': 'Gemini API is temporarily unavailable (503). Please try again later.',
                            'error_code': 503,
                            'details': 'The service may be overloaded or under maintenance.'
                        }, 503
                    elif response.status_code == 429:
                        return {
                            'message': 'Rate limit exceeded. Please try again later.',
                            'error_code': 429
                        }, 429
                    elif response.status_code == 400:
                        return {
                            'message': 'Bad request to Gemini API. Please check your input.',
                            'error_code': 400,
                            'details': response.text
                        }, 400
                    else:
                        return {
                            'message': f'Gemini API error: {response.status_code}',
                            'error_code': response.status_code,
                            'details': response.text
                        }, 500
                
                # Parse the response
                result = response.json()
                
                # Extract the generated text
                try:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    # Convert markdown to plain text if requested
                    if convert_markdown:
                        final_text = markdown_to_plain_text(generated_text)
                    else:
                        final_text = generated_text
                    user_id = g.current_user.uid if hasattr(g, 'current_user') and g.current_user else 'anonymous'
                    return {
                        'success': True,
                        'text': final_text,
                        'user': user_id
                    }
                except (KeyError, IndexError) as e:
                    current_app.logger.error(f"Error parsing Gemini response: {e}")
                    return {
                        'success': False,
                        'message': 'Error parsing Gemini API response',
                        'raw_response': result
                    }, 500
                    
            except requests.RequestException as e:
                current_app.logger.error(f"Error communicating with Gemini API: {e}")
                return {'message': f'Error communicating with Gemini API: {str(e)}'}, 500
            except Exception as e:
                current_app.logger.error(f"Unexpected error in Gemini API: {e}")
                return {'message': f'Unexpected error: {str(e)}'}, 500

    class _Health(Resource):
        """
        Health check endpoint for Gemini API integration.
        """
        # @token_required()  # Temporarily disabled for testing
        def get(self):
            """
            Check if Gemini API is properly configured.
            
            Returns:
                JSON response indicating configuration status
            """
            api_key = app.config.get('GEMINI_API_KEY')
            server = app.config.get('GEMINI_SERVER')
            
            # Test the API endpoint if configured
            status_info = {
                'gemini_configured': bool(api_key and server),
                'server': server if server else 'Not configured',
                'api_key_present': bool(api_key)
            }
            
            if api_key and server:
                try:
                    # Make a simple test request to check API availability
                    test_endpoint = f"{server}?key={api_key}"
                    test_payload = {
                        "contents": [{
                            "parts": [{"text": "Hello"}]
                        }]
                    }
                    
                    response = requests.post(
                        test_endpoint,
                        headers={'Content-Type': 'application/json'},
                        json=test_payload,
                        timeout=10
                    )
                    
                    status_info['api_test'] = {
                        'status_code': response.status_code,
                        'available': response.status_code == 200
                    }
                    
                    if response.status_code != 200:
                        status_info['api_test']['error'] = response.text
                        
                except Exception as e:
                    status_info['api_test'] = {
                        'available': False,
                        'error': str(e)
                    }
            
            return status_info

    class _Debug(Resource):
        """
        Debug endpoint to help troubleshoot Gemini API issues.
        """
        # @token_required()  # Temporarily disabled for testing
        def post(self):
            """
            Debug the Gemini API request to identify 503 issues.

            Returns detailed information about the request and response.
            """
            user_id = g.current_user.uid if hasattr(g, 'current_user') and g.current_user else 'anonymous'
            body = request.get_json()

            # Get configuration
            api_key = app.config.get('GEMINI_API_KEY')
            server = app.config.get('GEMINI_SERVER')

            debug_info = {
                'user': user_id,
                'config_check': {
                    'api_key_present': bool(api_key),
                    'api_key_length': len(api_key) if api_key else 0,
                    'server': server,
                    'server_valid': bool(server and server.startswith('https://'))
                },
                'request_body': body
            }
            
            if not api_key or not server:
                debug_info['error'] = 'Missing API configuration'
                return debug_info, 500
            
            # Build the endpoint URL
            endpoint = f"{server}?key={api_key}"
            debug_info['endpoint'] = endpoint
            
            # Simple test payload
            test_payload = {
                "contents": [{
                    "parts": [{"text": "Test"}]
                }]
            }
            
            try:
                response = requests.post(
                    endpoint,
                    headers={'Content-Type': 'application/json'},
                    json=test_payload,
                    timeout=30
                )
                
                debug_info['response'] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content': response.text[:500] if response.text else None  # Limit content length
                }
                
                return debug_info
                
            except Exception as e:
                debug_info['exception'] = str(e)
                return debug_info, 500

    # Register endpoints
    api.add_resource(_Ask, '/gemini')
    api.add_resource(_Health, '/gemini/health')
    api.add_resource(_Debug, '/gemini/debug')