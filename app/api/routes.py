from flask import Blueprint, request, jsonify
from ..utils.validation import validate_document_request

api = Blueprint('api', __name__)

@api.route('/documents', methods=['POST'])
def create_document():
    """Convert Notion page to DocuSign envelope"""
    data = validate_document_request(request.json)
    
    # TODO: Implement document creation
    return jsonify({
        'status': 'success',
        'message': 'Document creation not yet implemented'
    })

@api.route('/documents/<document_id>/status')
def get_document_status(document_id):
    """Get current status of a document"""
    # TODO: Implement status check
    return jsonify({
        'status': 'pending',
        'message': 'Status check not yet implemented'
    }) 