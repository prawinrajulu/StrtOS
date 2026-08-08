import re
from app.auth.exceptions import AuthException

class AuthValidator:
    """Password Policy & Input Validation."""
    
    @staticmethod
    def validate_password(password: str) -> bool:
        if len(password) < 8:
            raise AuthException("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise AuthException("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise AuthException("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise AuthException("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise AuthException("Password must contain at least one special character.")
        return True
