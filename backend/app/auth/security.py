from passlib.context import CryptContext

# Production bcrypt CryptContext (cost factor = 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityHandler:
    """Enterprise Password Hashing using bcrypt via Passlib."""

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

security_handler = SecurityHandler()
