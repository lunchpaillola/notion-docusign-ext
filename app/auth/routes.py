from flask import Blueprint, redirect, url_for, session, request, jsonify
from ..utils.errors import AuthError
from .utils import (
    get_notion_oauth_url, 
    get_docusign_oauth_url,
    exchange_notion_code,
    exchange_docusign_code,
    refresh_token
)
import jwt
from flask import current_app

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    """Start the OAuth flow by redirecting to Notion"""
    return redirect(get_notion_oauth_url())

@auth.route('/notion/authorize')
def notion_authorize():
    """Start Notion OAuth flow"""
    return redirect(get_notion_oauth_url())

@auth.route('/notion/callback')
def notion_callback():
    """Handle Notion OAuth callback"""
    # Verify state if provided
    state = request.args.get('state')
    if state and state != session.get('notion_state'):
        raise AuthError("Invalid state parameter")
    
    # Check for error
    error = request.args.get('error')
    if error:
        raise AuthError(f"Notion authorization failed: {error}")
    
    code = request.args.get('code')
    if not code:
        raise AuthError("No authorization code received from Notion")
    
    # Exchange code for access token
    token_data = exchange_notion_code(code)
    
    # Store tokens and workspace info securely
    session['notion_access_token'] = token_data['access_token']
    session['notion_workspace_id'] = token_data['workspace_id']
    session['notion_workspace_name'] = token_data.get('workspace_name')
    session['notion_bot_id'] = token_data['bot_id']
    
    # Redirect to DocuSign OAuth or dashboard
    return redirect(url_for('auth.docusign_authorize'))

@auth.route('/authorize')
def authorize():
    """Handle initial authorization request"""
    redirect_uri = request.args.get('redirect_uri')
    state = request.args.get('state')
    
    if not redirect_uri:
        raise AuthError("Missing redirect URI")
        
    # Store in session for validation in callback
    session['redirect_uri'] = redirect_uri
    session['state'] = state
    
    return redirect(get_docusign_oauth_url())

@auth.route('/token', methods=['POST'])
def token():
    """Handle token generation and refresh"""
    grant_type = request.form.get('grant_type')
    
    if grant_type == 'authorization_code':
        code = request.form.get('code')
        if not code:
            raise AuthError("Missing authorization code")
            
        token_data = exchange_docusign_code(code)
        return jsonify(token_data)
        
    elif grant_type == 'refresh_token':
        refresh_token_str = request.form.get('refresh_token')
        if not refresh_token_str:
            raise AuthError("Missing refresh token")
            
        token_data = refresh_token(refresh_token_str)
        return jsonify(token_data)
        
    raise AuthError("Invalid grant type")

@auth.route('/userinfo')
def userinfo():
    """Return user information from token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthError("Missing or invalid authorization header")
        
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return jsonify({
            'sub': payload['sub'],
            'email': payload['email']
        })
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token") 