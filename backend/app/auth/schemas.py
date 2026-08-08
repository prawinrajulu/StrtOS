from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.auth.models import UserRole, UserStatus, PermissionEnum

class UserRegisterRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=100)
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 900  # 15 minutes

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

class UserDTO(BaseModel):
    id: str
    organization_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_verified: bool
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

class OrganizationDTO(BaseModel):
    id: str
    name: str
    slug: str
    is_active: bool
    created_at: datetime

class UserSessionDTO(BaseModel):
    id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    last_activity: datetime
    created_at: datetime
