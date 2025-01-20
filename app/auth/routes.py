from flask import Blueprint, redirect, url_for, session, request, jsonify, render_template
from ..utils.errors import AuthError
from .utils import (
    get_notion_oauth_url, 
    get_docusign_oauth_url,
    exchange_notion_code,
    exchange_docusign_code,
    refresh_token,
    generate_access_token,
    generate_refresh_token
)
from ..supabase_db import (
    get_docusign_state,
    store_oauth_token,
    store_docusign_state,
    update_docusign_state
)
import jwt
from flask import current_app
from urllib.parse import urlencode

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
        return jsonify({
            'error': 'Invalid state parameter',
            'message': 'State not found in database',
            'state': state
        }), 400
    
    # Get Notion code
    code = request.args.get('code')
    if not code:
        print("❌ No code in request!")
        raise AuthError("No authorization code received from Notion")
    
    # Exchange code for access token
    token_data = exchange_notion_code(code)
    print("✅ Got Notion token:", token_data)
    
    # Store tokens and workspace info in Supabase
    store_result = store_oauth_token(
        state=state,
        notion_token=token_data['access_token'],
        workspace_id=token_data.get('workspace_id'),
        workspace_name=token_data.get('workspace_name')
    )
    print("Supabase store result:", store_result)
    
    # Store the DocuSign authorization code
    update_result = update_docusign_state(
        state=state, 
        authorization_code=current_app.config['AUTHORIZATION_CODE']
    )
    print("Authorization code storage result:", update_result)
    
    # Get DocuSign redirect info from stored state
    docusign_params = stored_state['params']
    print("DocuSign params for redirect:", docusign_params)
    
    redirect_url = f"{docusign_params['redirect_uri']}?code={current_app.config['AUTHORIZATION_CODE']}&state={docusign_params['state']}"
    print("Redirecting to:", redirect_url)
    
    return redirect(redirect_url)

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

# DocuSign Extension OAuth routes
@auth.route('/api/oauth/consent')
def oauth_consent():
    """Handle DocuSign Extension consent request"""
    redirect_uri = request.args.get('redirect_uri')
    state = request.args.get('state')
    
    if not redirect_uri:
        raise AuthError("Missing redirect URI")
    
    # Store in session for validation
    session['redirect_uri'] = redirect_uri
    session['state'] = state
    
    # Return consent page
    return render_template('consent.html', 
        redirect_uri=redirect_uri,
        code=current_app.config['AUTHORIZATION_CODE'],
        state=state
    )

@auth.route('/api/oauth/authorize')
def oauth_authorize():
    """Handle DocuSign Extension authorization"""
    # Store DocuSign params
    state = request.args.get('state')
    store_docusign_state(state, {
        'redirect_uri': request.args.get('redirect_uri'),
        'state': state
    })
    
    # Debug prints
    print("DocuSign params:", request.args)
    
    # Redirect to Notion OAuth
    notion_params = {
        'client_id': current_app.config.get('OAUTH_CLIENT_ID'),
        'response_type': 'code',
        'owner': 'user',
        'redirect_uri': current_app.config.get('NOTION_REDIRECT_URI'),
        'state': state
    }
    
    print("Notion params:", notion_params)
    
    return redirect(f"https://api.notion.com/v1/oauth/authorize?{urlencode(notion_params)}")

@auth.route('/api/oauth/token', methods=['POST'])
def oauth_token():
    """Handle token generation and refresh"""
    # Your token code...

@auth.route('/api/auth/test-db')
def test_db():
    """Test Supabase connection and tables"""
    try:
        supabase = get_supabase_client()
        
        # Test oauth_tokens table
        oauth_response = supabase.table('oauth_tokens').select("*").limit(1).execute()
        
        # Test docusign_states table
        docusign_response = supabase.table('docusign_states').select("*").limit(1).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'tables': {
                'oauth_tokens': 'accessible',
                'docusign_states': 'accessible'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@auth.route('/test-config')
def test_config():
    """Test Supabase configuration"""
    return jsonify({
        'supabase_url': current_app.config.get('SUPABASE_URL', 'Not set'),
        'supabase_key_set': bool(current_app.config.get('SUPABASE_KEY')),
    })

@auth.route('/routes')
def list_routes():
    """List all registered routes"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(routes)

@auth.route('/notion/callback/test')
def test_callback():
    """Test if callback route exists"""
    return jsonify({
        'status': 'success',
        'message': 'Notion callback route exists',
        'full_path': request.url,
        'blueprint_prefix': auth.url_prefix
    }) 