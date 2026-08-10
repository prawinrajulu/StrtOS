# StrtOS v1.0 — Governance Architecture & Decision Control System

## Overview
StrtOS v1.0 introduces the **Human Approval & AI Decision Governance Layer**. This layer ensures enterprise-grade decision control, compliance auditing, risk mitigation, and deterministic approval workflows for autonomous AI agent executions.

---

## Architecture Components

```
                      +-----------------------------+
                      |   StrtOS Frontend (Vite)    |
                      |  - ApprovalsPage.tsx        |
                      |  - ApprovalDetailsPage.tsx  |
                      +--------------+--------------+
                                     |
                                     | REST API / SSE
                                     v
                      +-----------------------------+
                      |  FastAPI Governance Router  |
                      |  /api/v1/governance/approvals|
                      +--------------+--------------+
                                     |
                +--------------------+--------------------+
                |                                         |
                v                                         v
+-------------------------------+       +-----------------------------------+
|  Governance Service           |       |  Deterministic Risk Engine        |
|  - Multi-tenant isolation     |       |  - Score: 0-100                   |
|  - Self-Approval Prevention   |<----->|  - Level: LOW, MEDIUM, HIGH,      |
|  - State Machine Enforcement  |       |           CRITICAL                |
+---------------+---------------+       +-----------------------------------+
                |
                +--------------------+
                |                    |
                v                    v
+-------------------------------+  +-----------------------------------+
| Live Supabase PostgreSQL DB   |  | Redis Pub/Sub & SSE Event Bus     |
| - approval_requests table     |  | - approval.created                |
| - auth_audit_logs table       |  | - approval.pending                |
| - FK & Row isolation          |  | - approval.approved / rejected    |
+-------------------------------+  +-----------------------------------+
```

---

## Key Features

1. **Approval Domain Model (`ApprovalRequestModel`)**:
   - Persisted in live Supabase PostgreSQL `approval_requests` table.
   - Enforces Foreign Key constraints (`organization_id`, `workflow_id`, `client_id`, `report_id`).
   - Supports 4 Risk Levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), 6 Decision Types, and 7 Approval Statuses.

2. **Deterministic Risk Engine (`risk_engine.py`)**:
   - Computes risk score (0–100) based on AI confidence score, evidence volume, action reversibility, AI execution health, and requested financial budget.
   - Automatically flags requests into risk tiers.

3. **Workflow Engine Integration (`WorkflowService`)**:
   - Automatically pauses workflows requiring approval (`status = PAUSED`, `active_stage = AWAITING HUMAN APPROVAL`).
   - Generates an `ApprovalRequestModel` record and broadcasts an SSE real-time notification (`approval.pending`).
   - Continues workflow execution to completion upon valid reviewer approval.

4. **Multi-Tenant Isolation & Role-Based Access Control (RBAC)**:
   - Organization-scoped queries (`organization_id == org_id`).
   - Approval actions restricted to `SUPER_ADMIN`, `ORG_ADMIN`, and `MANAGER` roles.
   - **Self-Approval Prevention**: Service-level rule forbidding requestors from approving their own governance requests.

5. **Real-Time SSE Sync & Dark Glass UI**:
   - React UI (`ApprovalsPage.tsx`, `ApprovalDetailsPage.tsx`) auto-refreshes in real-time via SSE event bus when approval state changes.
