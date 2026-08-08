from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
import uuid
from app.core.database import Base

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    VIEWER = "VIEWER"

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"

class PermissionEnum(str, enum.Enum):
    CREATE_WORKFLOW = "CREATE_WORKFLOW"
    DELETE_WORKFLOW = "DELETE_WORKFLOW"
    MANAGE_USERS = "MANAGE_USERS"
    MANAGE_ORGANIZATION = "MANAGE_ORGANIZATION"
    MANAGE_AGENTS = "MANAGE_AGENTS"
    VIEW_REPORTS = "VIEW_REPORTS"
    EXPORT_REPORTS = "EXPORT_REPORTS"
    BILLING_ACCESS = "BILLING_ACCESS"
    DASHBOARD_ACCESS = "DASHBOARD_ACCESS"

role_permissions = Table(
    "auth_role_permissions",
    Base.metadata,
    Column("role_id", String, ForeignKey("auth_roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String, ForeignKey("auth_permissions.id", ondelete="CASCADE"), primary_key=True)
)

class OrganizationModel(Base):
    __tablename__ = "auth_organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    users = relationship("UserModel", back_populates="organization", cascade="all, delete-orphan")

class RoleModel(Base):
    __tablename__ = "auth_roles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    permissions = relationship("PermissionModel", secondary=role_permissions, back_populates="roles")

class PermissionModel(Base):
    __tablename__ = "auth_permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("RoleModel", secondary=role_permissions, back_populates="permissions")

class UserModel(Base):
    __tablename__ = "auth_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("auth_organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    organization = relationship("OrganizationModel", back_populates="users")
    sessions = relationship("UserSessionModel", back_populates="user", cascade="all, delete-orphan")

class RefreshTokenModel(Base):
    __tablename__ = "auth_refresh_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UserSessionModel(Base):
    __tablename__ = "auth_user_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("UserModel", back_populates="sessions")

class PasswordResetTokenModel(Base):
    __tablename__ = "auth_password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AuditLogModel(Base):
    __tablename__ = "auth_audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("auth_organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
