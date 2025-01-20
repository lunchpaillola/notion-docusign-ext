from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class OAuthToken(db.Model):
    __tablename__ = 'oauth_tokens'
    
    id = db.Column(db.String(36), primary_key=True)
    state = db.Column(db.String(100), unique=True)
    notion_token = db.Column(db.Text, nullable=False)
    workspace_id = db.Column(db.String(100))
    workspace_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocuSignState(db.Model):
    __tablename__ = 'docusign_states'
    
    id = db.Column(db.String(36), primary_key=True)
    state = db.Column(db.String(100), unique=True)
    params = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False) 