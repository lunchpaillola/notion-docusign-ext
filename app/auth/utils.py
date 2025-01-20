from urllib.parse import urlencode
from flask import current_app, url_for
import jwt  # This is PyJWT
import uuid
from datetime import datetime, timedelta
import requests
import base64
from ..utils.errors import AuthError

def get_notion_oauth_url():
    """Generate Notion OAuth URL"""
    params = {
        'client_id': current_app.config['OAUTH_CLIENT_ID'],
        'redirect_uri': current_app.config['NOTION_REDIRECT_URI'],
        'response_type': 'code',
        'owner': 'user'
    }
    return f"https://api.notion.com/v1/oauth/authorize?{urlencode(params)}"

def get_docusign_oauth_url():
    """Generate DocuSign OAuth URL"""
    base_url = "https://account-d.docusign.com/oauth/auth"  # Development
    
    params = {
        'client_id': current_app.config['DOCUSIGN_CLIENT_ID'],
        'response_type': 'code',
        'scope': 'signature',  # Basic scope for eSignature
        'redirect_uri': 'https://demo.services.docusign.net/act-gateway/v1.0/oauth/callback',
    }
    return f"{base_url}?{urlencode(params)}"

def exchange_notion_code(code):
    """Exchange authorization code for Notion access token"""
    token_url = "https://api.notion.com/v1/oauth/token"
    
    # Create credentials for Basic Auth
    auth = base64.b64encode(
        f"{current_app.config['OAUTH_CLIENT_ID']}:{current_app.config['OAUTH_CLIENT_SECRET']}".encode()
    ).decode()
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['NOTION_REDIRECT_URI']
    }
    
    print("Notion Token Exchange Request:")
    print(f"URL: {token_url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    response = requests.post(token_url, json=data, headers=headers)
    
    print("Notion Response:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if not response.ok:
        raise AuthError(f"Failed to exchange Notion code for token: {response.text}")
        
    return response.json()

def exchange_docusign_code(code):
    """Exchange authorization code for DocuSign access token"""
    token_url = "https://account-d.docusign.com/oauth/token"
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': current_app.config['DOCUSIGN_CLIENT_ID'],
        'client_secret': current_app.config['DOCUSIGN_CLIENT_SECRET']
    }
    
    response = requests.post(token_url, data=data)
    if not response.ok:
        raise AuthError("Failed to exchange code for token")
        
    token_data = response.json()
    
    # Generate our own JWT tokens
    access_token = generate_access_token()
    refresh_token = generate_refresh_token()
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 3600,
        'token_type': 'Bearer',
        'docusign_token': token_data  # Store original DocuSign token
    }

def generate_access_token():
    """Generate JWT access token"""
    payload = {
        'type': 'access_token',
        'sub': str(uuid.uuid4()),
        'email': f"{uuid.uuid4()}@test.com",
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def generate_refresh_token():
    """Generate JWT refresh token"""
    payload = {
        'type': 'refresh_token',
        'jti': str(uuid.uuid4())
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def refresh_token(refresh_token):
    """Handle token refresh"""
    try:
        payload = jwt.decode(
            refresh_token, 
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        if payload['type'] != 'refresh_token':
            raise AuthError("Invalid token type")
            
        return {
            'access_token': generate_access_token(),
            'refresh_token': generate_refresh_token(),
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
    except jwt.InvalidTokenError:
        raise AuthError("Invalid refresh token") 