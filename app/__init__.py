from flask import Flask
from flask_cors import CORS
from .auth.routes import auth
from .api.routes import api
from .webhooks.routes import webhooks

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webhooks, url_prefix='/webhooks')
    
    return app 