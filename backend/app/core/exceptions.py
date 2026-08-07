from typing import Optional

class BaseStrtOSException(Exception):
    def __init__(self, message: str, status_code: int = 400, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(BaseStrtOSException):
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, status_code=422, details=details)

class AuthenticationException(BaseStrtOSException):
    def __init__(self, message: str = "Invalid credentials or token expired", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)

class DatabaseException(BaseStrtOSException):
    def __init__(self, message: str = "Database operation failure", details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)

class WorkflowException(BaseStrtOSException):
    def __init__(self, message: str = "Workflow execution error", details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)

class RedisException(BaseStrtOSException):
    def __init__(self, message: str = "Redis event transport failure", details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)
