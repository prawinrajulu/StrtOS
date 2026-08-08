import asyncio
from app.auth.validator import AuthValidator
from app.auth.security import security_handler
from app.auth.jwt_handler import jwt_handler
from app.auth.exceptions import AuthException, TokenExpiredException, InvalidTokenException

def test_password_security_bcrypt():
    # Verify bcrypt hashing
    password = "EnterpriseSecurePass123!"
    hashed = security_handler.hash_password(password)
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert security_handler.verify_password(password, hashed) is True
    assert security_handler.verify_password("WrongPassword123!", hashed) is False

def test_password_policy_validation():
    assert AuthValidator.validate_password("SecurePass123!") is True
    try:
        AuthValidator.validate_password("short1!")
        assert False, "Should fail short length"
    except AuthException:
        pass

async def test_jwt_jti_and_claims():
    user_id = "usr-audit-1"
    org_id = "org-audit-1"
    role = "ORG_ADMIN"

    access_token = jwt_handler.create_access_token(user_id, org_id, role)
    payload = await jwt_handler.decode_and_verify_token(access_token)
    assert payload["sub"] == user_id
    assert payload["org_id"] == org_id
    assert "jti" in payload
    assert payload["type"] == "access"

    # Test Blacklisting
    await jwt_handler.blacklist_token(access_token)
    try:
        await jwt_handler.decode_and_verify_token(access_token)
        assert False, "Should fail on blacklisted token"
    except InvalidTokenException:
        pass
