from flask import Flask
from flask_cors import CORS
from .auth.routes import auth
from .api.routes import api
from .api.oauth import oauth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load config
    app.config.from_object('config.Config')
    
    # Debug print
    print("Loaded config:", {
        key: value for key, value in app.config.items() 
        if not key.startswith('_')
    })
    
    # Set Flask secret key for sessions
    app.secret_key = os.getenv('JWT_SECRET_KEY')  # Using our JWT secret for Flask sessions
    
    # Load config from environment
    app.config.update(
        AUTHORIZATION_CODE=os.getenv('AUTHORIZATION_CODE'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
        OAUTH_CLIENT_ID=os.getenv('OAUTH_CLIENT_ID'),
        OAUTH_CLIENT_SECRET=os.getenv('OAUTH_CLIENT_SECRET')
    )
    
    # Register blueprints with correct prefixes
    app.register_blueprint(auth, url_prefix='/api/auth')  # This makes /notion/callback -> /api/auth/notion/callback
    app.register_blueprint(oauth, url_prefix='/api/oauth')
    
    return app 