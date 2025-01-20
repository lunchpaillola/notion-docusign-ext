from flask import Flask
from flask_cors import CORS
from .auth.routes import auth
from .api.routes import api
from .webhooks.routes import webhooks
from .api.oauth import oauth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load config from environment
    app.config.update(
        AUTHORIZATION_CODE=os.getenv('AUTHORIZATION_CODE'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
        OAUTH_CLIENT_ID=os.getenv('OAUTH_CLIENT_ID'),
        OAUTH_CLIENT_SECRET=os.getenv('OAUTH_CLIENT_SECRET')
    )
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webhooks, url_prefix='/webhooks')
    app.register_blueprint(oauth)
    
    return app 