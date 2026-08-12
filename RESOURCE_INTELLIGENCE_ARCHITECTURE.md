# StrtOS v2.6.0 — Autonomous Resource & Capacity Intelligence

## Architecture

```
REAL BUSINESS STATE
        ↓
PORTFOLIO (v2.5) / MISSIONS (v2.4)
        ↓
MISSION RESOURCE REQUIREMENTS
   (MissionCapacityAnalyzer)
        ↓
RESOURCE POOL
   (ResourceModel — HUMAN, AI_AGENT, BUDGET, TIME, COMPUTE, TOOL,
    EXECUTION_CAPACITY, MARKETING_CAPACITY, OPERATIONAL_CAPACITY)
        ↓
CAPACITY ENGINE          BOTTLENECK ENGINE         CONFLICT ENGINE
(utilization formula)    (shortage detection)      (concurrent demand)
        ↓                       ↓                        ↓
RESOURCE PRIORITY ENGINE (strategic value ranking)
        ↓
OPPORTUNITY COST ENGINE (what-if comparative analysis)
        ↓
ALLOCATION ENGINE (deterministic greedy, priority-scored)
        ↓
WHAT-IF SIMULATION ENGINE (side-effect free)
        ↓
ALLOCATION PLAN (with version history)
        ↓
RISK EVALUATION
        ↓
GOVERNANCE (GovernanceService — when risk ≥ 70 or bottleneck CRITICAL)
        ↓
EventPublisher (11 SSE events)
        ↓
MISSION EXECUTION (v2.4 ExecutionEngine)
```

---

## Resource Domain

### ResourceModel — 9 types
| Type | Description |
|---|---|
| HUMAN | Human team capacity |
| AI_AGENT | Autonomous agent capacity |
| BUDGET | Financial budget (USD/currency) |
| TIME | Time capacity (hours) |
| COMPUTE | Compute resources (CPU/GPU) |
| TOOL | Tool availability |
| EXECUTION_CAPACITY | Execution slot capacity |
| MARKETING_CAPACITY | Marketing channel capacity |
| OPERATIONAL_CAPACITY | Operational bandwidth |

### ResourceStatus
`AVAILABLE` · `LIMITED` (≥75%) · `EXHAUSTED` (≥100%) · `BLOCKED` · `DEGRADED` · `UNKNOWN` (when total_capacity is NULL)

Never assumes capacity. `total_capacity = NULL → status = UNKNOWN`.

---

## Database Schema

```
resources
  ├── resource_capacities        (time-series snapshots, is_measured flag)
  ├── resource_allocations       (immutable per-mission records)
  ├── resource_constraints       (hard/soft constraint tracking)
  ├── resource_conflicts         (detected conflicts with resolution options)
  ├── resource_utilizations      (running utilization snapshots)
  ├── resource_allocation_plans  (full plan lifecycle with version history)
  └── resource_allocation_plan_versions (immutable version records)
```

All 8 tables: `organization_id NOT NULL` · `created_at` · indexes on `organization_id, resource_type, status, mission_id, created_at`.

---

## Capacity Engine

**Formulas (deterministic)**:
```
utilization_pct = allocated / total × 100
remaining       = max(0, total - allocated)
shortage        = max(0, allocated - total)
status          = UNKNOWN if total is None or 0
               | EXHAUSTED if utilization ≥ 100%
               | LIMITED if utilization ≥ 75%
               | AVAILABLE otherwise
```

Measured vs. estimated: `is_measured=True` when capacity comes from actual system telemetry.

---

## Bottleneck Detection

Aggregates all mission requirements per resource. Computes available = `max(0, total - allocated)`.  
Shortage = `max(0, required - available)`.

**Severity**:
| Shortage % | Severity |
|---|---|
| ≥ 50% | CRITICAL |
| ≥ 25% | HIGH |
| ≥ 10% | MEDIUM |
| < 10% | LOW |

Returns: `resource, current_capacity, required_capacity, shortage, affected_missions, severity, recommended_action`.

---

## Conflict Engine

Triggers when 2+ missions request the same resource concurrently. Combined demand > available → CONFLICT.  
Returns `conflict_id, mission_ids, shortage, severity, resolution_options`.

**Resolution options** are severity-graded (CRITICAL → ESCALATE governance, LOW → monitor).

---

## Allocation Engine

**Algorithm**: Deterministic greedy allocation by priority score.

**Priority score weights**:
| Factor | Weight |
|---|---|
| Strategic Value | 25% |
| Expected Value (normalized) | 20% |
| Urgency | 15% |
| Mission Priority | 15% |
| Confidence | 10% |
| Risk (inverted) | 10% |
| Resource Efficiency | 5% |

Missions sorted by score. Each mission's mandatory resources attempted in order. Failed mandatory resource → mission RESOURCE_CONSTRAINED.  
Every allocation includes a full text explanation.

---

## Opportunity Cost Engine

Calculates the value lost by choosing Mission A over Mission B.

```
opportunity_cost_score = max(0, EV_alternative - EV_selected) / EV_alternative × 100
```

Returns `INSUFFICIENT_DATA` when inputs are missing — never fabricates values.

---

## What-If Simulation

**Side-effect free**: operates on in-memory copy of resource pool only. No DB mutations.

Supported scenarios:
- `CURRENT_CAPACITY`
- `+10_PERCENT_CAPACITY` / `-10_PERCENT_CAPACITY`
- `+20_PERCENT_BUDGET` / `-20_PERCENT_BUDGET`
- `ADDITIONAL_HUMAN_CAPACITY`
- `ADDITIONAL_AGENT_CAPACITY`
- `REDUCED_EXECUTION_CAPACITY`
- `CUSTOM`

Returns: feasible missions, blocked missions, bottlenecks, utilization, expected value, opportunity cost, strategic impact summary, recommendation.

---

## Allocation Plan Lifecycle

```
DRAFT → SIMULATED → PENDING_GOVERNANCE (risk ≥ 70 or CRITICAL bottleneck)
                  ↓
               APPROVED → ACTIVE → COMPLETED
               REJECTED
               ROLLED_BACK
```

Immutable version history: each plan change creates a new `ResourceAllocationPlanVersionModel` linked by `parent_version`.

---

## Governance Integration

Uses existing `GovernanceService.create_approval_request()` — no new approval system.

**Governance gate triggers**:
- Risk score ≥ 70
- CRITICAL bottleneck detected
- Large budget allocation
- Cross-client resource reallocation
- Policy-restricted resource

Workflow: `Recommendation → Risk Evaluation → GovernanceService → Human Approval → activate_plan()`.

---

## Mission Integration

`MissionCapacityAnalyzer` maps mission step `action_type` to resource requirements:
- Explicit step `resource_requirements_json` takes precedence
- Falls back to `ACTION_TYPE_REQUIREMENTS` defaults (RUN_SEO_AUDIT, CREATE_CAMPAIGN, GENERATE_REPORT, EXECUTE_WORKFLOW, HUMAN_REVIEW)
- Returns feasibility: `FEASIBLE | AT_RISK | INFEASIBLE | UNKNOWN`

---

## API Reference

```
GET  /api/v1/resources/overview
GET  /api/v1/resources/resources
POST /api/v1/resources/resources
GET  /api/v1/resources/resources/{id}
GET  /api/v1/resources/capacity
GET  /api/v1/resources/utilization
GET  /api/v1/resources/bottlenecks
GET  /api/v1/resources/conflicts
GET  /api/v1/resources/allocations
POST /api/v1/resources/allocations/simulate
POST /api/v1/resources/allocations/recommend
POST /api/v1/resources/allocations/plan
GET  /api/v1/resources/allocations/{id}
GET  /api/v1/resources/allocations/{id}/explanation
POST /api/v1/resources/allocations/{id}/submit-governance
POST /api/v1/resources/allocations/{id}/approve
POST /api/v1/resources/allocations/{id}/activate
GET  /api/v1/resources/missions/{mission_id}/resources
```

All endpoints: JWT authenticated · RBAC · organization_id isolated.

---

## SSE Events (11)

```
resource.created
resource.updated
resource.capacity.changed
resource.bottleneck.detected
resource.conflict.detected
resource.allocation.simulated
resource.allocation.recommended
resource.allocation.governance_pending
resource.allocation.approved
resource.allocation.activated
resource.allocation.failed
```

Uses existing `EventPublisher` → Redis → SSE infrastructure.

---

## Security

- All routes: `Depends(get_current_user)` — no unauthenticated access
- `organization_id` extracted from JWT and enforced on every query
- No cross-tenant FK references possible
- GovernanceService mandatory on risk ≥ 70 — no bypass possible
- `total_capacity = NULL → UNKNOWN` — no invented capacity
- `INSUFFICIENT_DATA` returned when opportunity cost inputs missing
- No secrets, no eval/exec, no hardcoded credentials
- Simulation: `is_side_effect_free=True` guaranteed (in-memory only)

---

## Tests (92 passed)

| Class | Tests |
|---|---|
| TestResourceModels | 9 — enum values, table names, org_id nullability, column presence |
| TestCapacityEngine | 15 — utilization formula, status thresholds, determinism, edge cases |
| TestBottleneckEngine | 8 — shortage detection, severity, affected missions, unknown capacity |
| TestConflictEngine | 5 — single-mission (no conflict), combined demand, resolution options |
| TestPriorityEngine | 8 — score range, determinism, high risk penalized, rank uniqueness |
| TestOpportunityCostEngine | 7 — sufficient data, insufficient data, EV/resource/risk diffs |
| TestResourceAllocationEngine | 9 — greedy allocation, priority order, pool never negative |
| TestResourceSimulationEngine | 5 — side-effect free, scenario modifiers, recommendation |
| TestMissionCapacityAnalyzer | 5 — defaults, explicit overrides, feasibility |
| TestResourceSchemas | 4 — create, simulation, plan schemas |
| TestTenantIsolation | 5 — org_id NOT NULL on all 5 model types |
| TestResourceAPI | 10 — all endpoints require authentication |
| TestAppVersion | 2 — version 2.6.0, router mounted |
