# StrtOS v1.3.0 — Autonomous Execution & Closed-Loop Optimization Architecture

## Overview
StrtOS v1.3.0 introduces **Autonomous Execution & Closed-Loop Optimization**. This milestone upgrades StrtOS from a predictive model into a closed-loop execution operating system. Every AI proposed action passes through an explicit `ActionRegistry`, deterministic `PolicyEngine`, and existing `Governance` approval layer before execution via the `ToolRegistry`. Execution telemetry automatically feeds into outcome variance evaluation, prediction accuracy scoring, memory record creation, and closed-loop optimization.

---

## Execution Loop Architecture Diagram

```
                    ┌───────────────┐
                    │ CEO / AI      │
                    │ Decision      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Prediction    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Action        │
                    │ Proposal      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Policy Engine │
                    └───────┬───────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Human Governance     │
                 │ Approval if required │
                 └──────────┬───────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Action        │
                    │ Executor      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Tool Registry │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Real Tool/API │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Measurement   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Memory/Lesson │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Optimization  │
                    └───────────────┘
```

---

## Security & Safety Rules

1. **No Arbitrary Code / Shell Execution**:
   - LLM output is NEVER directly executable.
   - The AI does not receive shell access, SQL access, Python eval, or arbitrary external HTTP access.
   - All execution MUST pass through `ActionRegistry` allowlists.

2. **Autonomy Modes**:
   - `MANUAL`: Human explicitly initiates action.
   - `ASSISTED`: AI proposes action, human confirms before execution.
   - `APPROVAL_REQUIRED`: Policy engine creates governance approval; execution is blocked until explicit reviewer approval.
   - `AUTONOMOUS`: Only allowlisted `LOW` risk actions can execute automatically.
   - `HIGH` and `CRITICAL` risk actions NEVER execute autonomously.

3. **Idempotency Protection**:
   - Every action requires an `idempotency_key` (e.g. `org_id + workflow_id + action_type + prediction_id`). Duplicate requests return the existing action without duplicate tool execution.

4. **Multi-Tenant & Role Isolation**:
   - All queries scope `organization_id == current_user.organization_id`.
   - Cross-tenant actions or unauthorized roles return `PolicyDecision.DENY`.
   - Self-approval prevention is strictly enforced.

---

## Key Components

1. **Database Model (`ActionModel`)**:
   - Mapped to `actions` table in live Supabase PostgreSQL (26 columns, 10 indexes).
   - Foreign keys to `organizations`, `clients`, `workflows`, `predictions`, `approval_requests`.

2. **Action Registry (`action_registry.py`)**:
   - Explicit allowlist of safe actions (`GENERATE_REPORT`, `RUN_WEBSITE_AUDIT`, `RUN_SEO_AUDIT`, `RUN_COMPETITOR_RESEARCH`, `COLLECT_BUSINESS_DATA`, `REFRESH_CLIENT_ANALYSIS`, `RUN_PAGESPEED_ANALYSIS`, `CREATE_CAMPAIGN_DRAFT`, `GENERATE_MARKETING_PLAN`, `RECORD_OUTCOME`).

3. **Policy Engine (`policy_engine.py`)**:
   - Deterministic policy evaluator assigning `ALLOW`, `DENY`, or `REQUIRE_APPROVAL`.

4. **Closed-Loop Optimization Engine (`measurement.py`)**:
   - Evaluates action execution performance against prediction targets, computes accuracy scores, maps outcome status (`SUCCESS`, `PARTIAL`, `FAILED`), and records grounded lessons in v1.1 Memory.

5. **Real-Time SSE Events**:
   - Emits `action.created`, `action.started`, `action.completed`, `action.failed`, `outcome.recorded`, and `optimization.completed`.
