import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Environment
    NODE_ENV = os.getenv('NODE_ENV', 'development')
    PORT = int(os.getenv('PORT', 3000))
    
    # OAuth
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    AUTHORIZATION_CODE = os.getenv('AUTHORIZATION_CODE')
    
    # Redirect URIs
    NOTION_REDIRECT_URI = os.getenv('NOTION_REDIRECT_URI')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False 