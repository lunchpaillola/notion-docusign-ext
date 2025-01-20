from flask import Blueprint, request, jsonify
from ..utils.validation import validate_document_request
from .transforms import notion_to_docusign_transform

api = Blueprint('api', __name__)

@api.route('/documents', methods=['POST'])
def create_document():
    """Convert Notion page to DocuSign envelope"""
    data = validate_document_request(request.json)
    
    # Transform Notion content to DocuSign format
    docusign_content = notion_to_docusign_transform(
        notion_page_id=data['notionPageId']
    )
    
    # Create envelope in DocuSign
    envelope_id = create_docusign_envelope(docusign_content)
    
    return jsonify({
        'status': 'success',
        'envelopeId': envelope_id
    })

@api.route('/documents/<document_id>/status')
def get_document_status(document_id):
    """Get current status of a document"""
    document = Document.get(document_id)
    return jsonify({
        'status': document.status,
        'signatureUrl': document.signatureUrl,
        'archivedFileUrl': document.archivedFileUrl
    }) 