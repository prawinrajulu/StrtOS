from fastapi import HTTPException, status

class AuthException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid email or password.", status_code=status.HTTP_401_UNAUTHORIZED)

class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__(detail="Token has expired.", status_code=status.HTTP_401_UNAUTHORIZED)

class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid token provided.", status_code=status.HTTP_401_UNAUTHORIZED)

class UserAlreadyExistsException(AuthException):
    def __init__(self):
        super().__init__(detail="User with this email already exists.", status_code=status.HTTP_409_CONFLICT)

class AccessDeniedException(AuthException):
    def __init__(self, detail: str = "Access denied: insufficient permissions."):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)
