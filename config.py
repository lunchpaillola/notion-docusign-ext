import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Notion
    NOTION_CLIENT_ID = os.getenv('NOTION_CLIENT_ID')
    NOTION_CLIENT_SECRET = os.getenv('NOTION_CLIENT_SECRET')
    NOTION_REDIRECT_URI = os.getenv('NOTION_REDIRECT_URI')
    
    # DocuSign
    DOCUSIGN_CLIENT_ID = os.getenv('DOCUSIGN_CLIENT_ID')
    DOCUSIGN_CLIENT_SECRET = os.getenv('DOCUSIGN_CLIENT_SECRET')
    DOCUSIGN_REDIRECT_URI = os.getenv('DOCUSIGN_REDIRECT_URI')
    DOCUSIGN_AUTH_SERVER = os.getenv('DOCUSIGN_AUTH_SERVER', 'account-d.docusign.com')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False 