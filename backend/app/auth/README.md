# Enterprise Auth & Multi-Tenant RBAC Module - StrtOS

The **Auth Module** (`backend/app/auth/`) provides enterprise-grade, multi-tenant authentication and Role-Based Access Control (RBAC) for StrtOS.

## Features

- **Multi-Tenant Organizations**: Isolates users, workflows, and executive reports by `organization_id`.
- **JWT Security**: Short-lived 15-minute access tokens and 7-day refresh tokens with rotation support.
- **Password Policy Enforcement**: Validates length ($\ge 8$), uppercase, lowercase, numbers, and special characters.
- **RBAC Roles**: `SUPER_ADMIN`, `ORG_ADMIN`, `MANAGER`, `EMPLOYEE`, `VIEWER`.
- **Audit Logging**: Logs login events, failed attempts, and role updates to `auth_audit_logs`.

## Module Structure

```
backend/app/auth/
├── models.py        # SQLAlchemy 2.0 Models (Organization, User, Role, Permission, Session, AuditLog)
├── schemas.py       # Pydantic v2 Input & Response DTOs
├── repository.py    # Async AuthRepository for DB operations
├── service.py       # AuthService executing register, login, session workflows
├── validator.py     # Password policy validator
├── security.py      # SHA256/Salt password hashing & verification
├── jwt_handler.py   # JWT Access & Refresh token generator/decoder
├── dependencies.py # FastAPI dependencies for user, org, & RBAC checks
├── routes.py       # REST Endpoints (/register, /login, /me, /sessions, etc.)
├── exceptions.py   # Auth & Permission HTTP Exceptions
└── README.md
```
