from ..models import Document
from ..utils.errors import WebhookError

def handle_docusign_webhook(event_data):
    """Handle DocuSign signature completion webhook"""
    envelope_id = event_data.get('envelopeId')
    if not envelope_id:
        raise WebhookError("No envelope ID in webhook")
        
    # Update document status
    document = Document.find_by_envelope_id(envelope_id)
    document.status = 'signed'
    document.signatureUrl = event_data.get('signedDocumentUrl')
    document.save()
    
    # Archive document if needed
    if document.status == 'signed':
        archive_document(document) 