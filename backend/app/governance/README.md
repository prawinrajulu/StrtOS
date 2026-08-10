# StrtOS Governance Module

The Governance module implements Human Approval & AI Decision Governance for StrtOS v1.0.

## Key Features
- **Approval Domain Model**: `ApprovalRequestModel` with multi-tenant isolation.
- **Deterministic Risk Engine**: `calculate_decision_risk` producing 0–100 risk score and `RiskLevel` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **State Machine**: Enforces strict state transitions (`PENDING_APPROVAL` -> `APPROVED` / `REJECTED` / `CHANGES_REQUESTED` / `CANCELLED`).
- **Self-Approval Prevention**: Service-level enforcement prohibiting requestors from approving their own requests.
- **RBAC**: Requires `SUPER_ADMIN`, `ORG_ADMIN`, or `MANAGER` role for approval actions.
