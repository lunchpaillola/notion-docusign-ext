from .errors import ValidationError

def validate_document_request(data):
    """Validate incoming document creation requests"""
    if not data:
        raise ValidationError("Request body cannot be empty")
    
    required_fields = ['notionPageId']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
            
    return data 