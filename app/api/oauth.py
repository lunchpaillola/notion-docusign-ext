from flask import Blueprint, request, jsonify, render_template, current_app
from ..utils.errors import AuthError
from ..auth.utils import generate_access_token, generate_refresh_token, refresh_token

oauth = Blueprint('oauth', __name__, url_prefix='/api/oauth')

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

@oauth.route('/token', methods=['POST'])
def token():
    """Handle token generation and refresh for DocuSign Extension"""
    grant_type = request.form.get('grant_type')
    
    if grant_type == 'authorization_code':
        code = request.form.get('code')
        if code != current_app.config['AUTHORIZATION_CODE']:
            raise AuthError("Invalid authorization code")
            
        # Generate new tokens
        access_token = generate_access_token()
        refresh_token = generate_refresh_token()
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token
        }) 