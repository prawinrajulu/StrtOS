import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import os
from app.auth.exceptions import TokenExpiredException, InvalidTokenException
from app.core.redis import redis_manager

JWT_SECRET = os.getenv("JWT_SECRET", "strtos-enterprise-secret-key-change-in-prod-2026")
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

class JWTHandler:
    """Enterprise JWT Access & Refresh Token Generator, Verifier, and Redis Blacklist Manager."""

    @staticmethod
    def create_access_token(user_id: str, org_id: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())
        payload = {
            "sub": user_id,
            "org_id": org_id,
            "role": role,
            "jti": jti,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())
        payload = {
            "sub": user_id,
            "jti": jti,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    async def decode_and_verify_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            jti = payload.get("jti")
            
            # Check Redis Blacklist
            if jti and await redis_manager.get(f"jwt_blacklist:{jti}"):
                raise InvalidTokenException()
                
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.PyJWTError:
            raise InvalidTokenException()

    @staticmethod
    async def blacklist_token(token: str):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                ttl = max(1, int(exp - datetime.now(timezone.utc).timestamp()))
                await redis_manager.set(f"jwt_blacklist:{jti}", "revoked", expire_seconds=ttl)
        except Exception:
            pass

jwt_handler = JWTHandler()
