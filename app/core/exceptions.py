"""
Custom Exception Classes

Defines application-specific exceptions for consistent error handling.
"""

from typing import Optional, Dict, Any


class AppException(Exception):
    """Base exception for application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(AppException):
    """Raised when user lacks permission."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class NotFoundError(AppException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID {resource_id} not found"
        super().__init__(message=message, status_code=404)


class ValidationError(AppException):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(message=message, status_code=422, details=details)


class ConflictError(AppException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=429)


class AIServiceError(AppException):
    """Raised when AI service fails."""
    
    def __init__(self, message: str = "AI service error", details: Optional[Dict] = None):
        super().__init__(message=message, status_code=503, details=details)


class DatabaseError(AppException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(message=message, status_code=500)
