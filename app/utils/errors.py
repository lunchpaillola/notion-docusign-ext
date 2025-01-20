class BaseError(Exception):
    """Base error class for the application"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthError(BaseError):
    """Raised when authentication fails"""
    pass

class ValidationError(BaseError):
    """Raised when request validation fails"""
    pass

class WebhookError(BaseError):
    """Raised when webhook processing fails"""
    pass 