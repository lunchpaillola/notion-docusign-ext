from flask import Blueprint, redirect, url_for, session, request
from ..utils.errors import AuthError
from .utils import get_notion_oauth_url, get_docusign_oauth_url

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    """Start the OAuth flow by redirecting to Notion"""
    return redirect(get_notion_oauth_url())

@auth.route('/notion/callback')
def notion_callback():
    """Handle Notion OAuth callback and start DocuSign OAuth"""
    code = request.args.get('code')
    if not code:
        raise AuthError("No authorization code received")
    
    # Store Notion credentials
    session['notion_token'] = code
    
    # Redirect to DocuSign OAuth
    return redirect(get_docusign_oauth_url())

@auth.route('/docusign/callback')
def docusign_callback():
    """Complete the OAuth flow by handling DocuSign callback"""
    code = request.args.get('code')
    if not code:
        raise AuthError("No authorization code received")
    
    # Store DocuSign credentials and complete setup
    session['docusign_token'] = code
    
    return redirect(url_for('dashboard')) 