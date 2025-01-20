from flask import Blueprint, request, jsonify, render_template, current_app, url_for, redirect, session
from ..utils.errors import AuthError
from ..utils.oauth_utils import (
    exchange_notion_code,
    generate_access_token,
    generate_refresh_token,
    refresh_token
)
from urllib.parse import urlencode
from collections import defaultdict
from ..supabase_db import store_oauth_token, store_docusign_state, get_oauth_token, get_docusign_state, get_oauth_token_by_code
import os
import jwt
from datetime import datetime, timedelta

oauth = Blueprint('oauth', __name__)
temp_storage = defaultdict()  # Simple in-memory storage

@oauth.route('/consent', methods=['GET'])
def consent():
    """Handle DocuSign Extension consent request"""
    # Get all OAuth parameters from DocuSign
    response_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope')
    state = request.args.get('state')
    prompt = request.args.get('prompt')
    access_type = request.args.get('access_type')
    
    if not redirect_uri:
        raise AuthError("Missing redirect URI")
    
    # Return consent page with all necessary parameters
    return render_template('consent.html', 
        redirect_uri=redirect_uri,
        code=current_app.config['AUTHORIZATION_CODE'],
        state=state
    )

@oauth.route('/authorize')
def oauth_authorize():
    """Handle DocuSign Extension authorization"""
    # Debug prints
    print("All config:", {
        key: value for key, value in current_app.config.items() 
        if not key.startswith('_')  # Skip internal Flask configs
    })
    
    print("Environment variables:", {
        key: value for key, value in os.environ.items()
        if key in ['NOTION_REDIRECT_URI', 'OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET']
    })
    
    # Store DocuSign params
    state = request.args.get('state')
    store_docusign_state(state, {
        'redirect_uri': request.args.get('redirect_uri'),
        'state': state
    })
    
    # Debug the notion params before redirect
    notion_params = {
        'client_id': current_app.config.get('OAUTH_CLIENT_ID'),
        'response_type': 'code',
        'owner': 'user',
        'redirect_uri': current_app.config.get('NOTION_REDIRECT_URI'),  # Use .get() instead
        'state': state
    }
    print("Notion params:", notion_params)
    
    return redirect(f"https://api.notion.com/v1/oauth/authorize?{urlencode(notion_params)}")

@oauth.route('/notion/callback')  # This will match /api/auth/notion/callback
def notion_callback():
    """Handle Notion callback"""
    print("\n=== Notion Callback Hit ===")
    print("URL:", request.url)
    print("Method:", request.method)
    print("Args:", request.args)
    
    # Get state from URL
    state = request.args.get('state')
    print("State from URL:", state)
    
    # Debug Supabase state
    stored_state = get_docusign_state(state)
    print("Stored state in Supabase:", stored_state)
    
    if not stored_state:
        print("❌ No state found in database!")
        raise AuthError("Invalid state")
    
    # Get Notion code
    code = request.args.get('code')
    if not code:
        print("❌ No code in request!")
        raise AuthError("No authorization code received from Notion")
    
    # Exchange code for access token
    token_data = exchange_notion_code(code)
    print("✅ Got Notion token:", token_data)
    
    # Store tokens and workspace info in Supabase
    store_oauth_token(
        state=state,
        notion_token=token_data['access_token'],
        workspace_id=token_data.get('workspace_id'),
        workspace_name=token_data.get('workspace_name')
    )
    
    # Redirect back to DocuSign with our authorization code
    return redirect(
        f"{stored_state['params']['redirect_uri']}?code={current_app.config['AUTHORIZATION_CODE']}&state={state}"
    )

@oauth.route('/token', methods=['POST'])
def oauth_token():
    """Handle token exchange"""
    print("\n=== Token Exchange Request ===")
    print("Form data:", request.form)
    print("Headers:", request.headers)
    
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    
    print(f"Grant Type: {grant_type}")
    print(f"Code: {code}")
    
    if grant_type == 'authorization_code':
        # Look up state by authorization code
        token_data = get_oauth_token_by_code(code)
        print("Token data from Supabase:", token_data)
        
        if not token_data:
            print("❌ No token data found for code:", code)
            raise AuthError("Notion authorization required")
            
        # Create a dummy refresh token that encodes the Notion token
        refresh_token = jwt.encode(
            {
                'notion_token': token_data.get('notion_token'),
                'exp': datetime.utcnow() + timedelta(days=365)  # Long expiry since Notion tokens don't expire
            },
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
            
        response_data = {
            'access_token': token_data.get('notion_token'),
            'token_type': 'Bearer',
            'refresh_token': refresh_token,  # Required by DocuSign
            'expires_in': 3600,  # Required by DocuSign
            'workspace_id': token_data.get('workspace_id'),
            'workspace_name': token_data.get('workspace_name')
        }
        print("✅ Returning response:", response_data)
        return jsonify(response_data)
    
    elif grant_type == 'refresh_token':
        # Handle refresh token flow
        refresh_token = request.form.get('refresh_token')
        if not refresh_token:
            raise AuthError("Missing refresh token")
            
        try:
            # Decode the refresh token to get the original Notion token
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Return the same Notion token since they don't expire
            return jsonify({
                'access_token': payload['notion_token'],
                'token_type': 'Bearer',
                'refresh_token': refresh_token,  # Return same refresh token
                'expires_in': 3600
            })
            
        except jwt.InvalidTokenError:
            raise AuthError("Invalid refresh token")
        
    print("❌ Invalid grant type:", grant_type)
    raise AuthError("Invalid grant type") 