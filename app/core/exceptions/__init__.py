class BaseAppException(Exception):
    """Base exception for all application exceptions"""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class EventNotFound(BaseAppException):
    """Exception raised when an event is not found"""
    pass

class CapacityExceeded(BaseAppException):
    """Exception raised when event capacity is exceeded"""
    pass

class DuplicateRegistration(BaseAppException):
    """Exception raised when attendee tries to register for the same event twice"""
    pass

class ValidationError(BaseAppException):
    """Exception raised for validation errors"""
    pass

__all__ = [
    "BaseAppException",
    "EventNotFound", 
    "CapacityExceeded",
    "DuplicateRegistration",
    "ValidationError"
]