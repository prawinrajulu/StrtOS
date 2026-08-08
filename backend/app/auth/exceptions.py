from app.core.exceptions import BaseStrtOSException

class AuthException(BaseStrtOSException):
    def __init__(self, message: str = "Authentication failed.", status_code: int = 400, details: dict = None):
        super().__init__(message=message, status_code=status_code, details=details)

class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(message="Invalid email or password.", status_code=401)

class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__(message="Token has expired.", status_code=401)

class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(message="Invalid token provided.", status_code=401)

class UserAlreadyExistsException(AuthException):
    def __init__(self):
        super().__init__(message="User with this email already exists.", status_code=409)

class AccessDeniedException(AuthException):
    def __init__(self, detail: str = "Access denied: insufficient permissions."):
        super().__init__(message=detail, status_code=403)
