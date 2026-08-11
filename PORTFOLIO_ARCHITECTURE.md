# StrtOS Portfolio Architecture

## Version: v2.5.0 — Autonomous Strategic Portfolio Management

StrtOS v2.5 transforms the system from *single-mission execution* into *multi-mission portfolio orchestration*: simultaneously managing multiple strategic missions across constrained resources, governed by deterministic scoring, bounded rebalancing, and GovernanceService sign-off.

---

## Core Portfolio Loop

```
BUSINESS STATE
      ↓
STRATEGIC OBJECTIVES
      ↓
ACTIVE MISSIONS
      ↓
MISSION PERFORMANCE (from v2.4 MissionEvaluationEngine)
      ↓
RESOURCE AVAILABILITY
      ↓
MISSION PRIORITY SCORING (PortfolioPriorityEngine)
      ↓
PORTFOLIO OPTIMIZATION (PortfolioOptimizationEngine — greedy knapsack)
      ↓
RESOURCE ALLOCATION (ResourceAllocationEngine)
      ↓
CONSTRAINT EVALUATION (PortfolioConstraintEngine)
      ↓
GOVERNANCE (GovernanceService — when risk ≥ 70 or budget ≥ 90%)
      ↓
MISSION EXECUTION (v2.4 MissionService)
      ↓
OUTCOME
      ↓
PORTFOLIO EVALUATION (PortfolioEvaluationEngine)
      ↓
REBALANCING (PortfolioRebalancingEngine — immutable versioning)
      ↺
```

---

## Portfolio Lifecycle

```
DRAFT → READY → ACTIVE → REBALANCING → ACTIVE
                ↓            ↓
          AWAITING_APPROVAL  AT_RISK
                ↓
           COMPLETED / FAILED / CANCELLED / ARCHIVED
```

Invalid state transitions are rejected by the service layer.

---

## Engine Architecture

### PortfolioConstraintEngine
Pure, stateless constraint evaluator.

| Utilization | Result |
|---|---|
| < 80% | VALID |
| 80–89% | WARNING |
| ≥ 90% (soft) | WARNING |
| ≥ 100% (hard) | VIOLATION |

### PortfolioPriorityEngine
Deterministic weighted scoring (0–100):

| Factor | Weight |
|---|---|
| Strategic Importance | 20% |
| Business Impact | 20% |
| Expected Value (normalized) | 15% |
| Success Probability | 15% |
| Urgency | 10% |
| Risk (inverted) | 10% |
| Resource Efficiency | 10% |

Priority labels: **CRITICAL** (≥80) · **HIGH** (≥60) · **MEDIUM** (≥40) · **LOW** (<40)

### PortfolioOptimizationEngine
Greedy knapsack: sort missions by `(expected_value × success_probability) / resource_requirement` then fill until budget/capacity exhausted.

Scenario capacity factors:
- **CONSERVATIVE**: 60% of available budget/capacity
- **BALANCED**: 80%
- **AGGRESSIVE**: 100%

Returns: selected, deferred, paused missions + explanation per mission.

### ResourceAllocationEngine
Per-mission resource allocator. Tracks: BUDGET, TIME, TEAM_CAPACITY, AGENT_CAPACITY, EXECUTION_CAPACITY.

On insufficient resources: `RESOURCE_CONSTRAINED` + recommendation (DEFER/REDUCE_SCOPE/PAUSE/REBALANCE/GOVERNANCE).

### PortfolioEvaluationEngine
```
health_score = 0.30 × mission_success_rate
             + 0.25 × (100 - risk_score)
             + 0.25 × confidence_score
             + 0.20 × resource_efficiency
```

Health labels: **EXCELLENT** (≥90) · **HEALTHY** (≥75) · **WATCH** (≥60) · **AT_RISK** (≥40) · **CRITICAL** (<40)

### PortfolioRebalancingEngine
Detects triggers: mission failed/completed, forecast delta ≥ 15%, risk crosses 70, resource change, objective shift.

Rebalancing creates an **immutable** new `PortfolioVersionModel` with parent_version link. The previous version is never mutated.

Governance gate: `risk ≥ 70` OR `budget_utilization ≥ 90%`.

### PortfolioCheckpointEngine

| Condition | Decision |
|---|---|
| progress ≥ 100% | COMPLETE |
| constraint violation | ESCALATE |
| CRITICAL health / risk ≥ 85 | ESCALATE |
| AT_RISK health / risk ≥ 70 | REBALANCE |
| WATCH + progress < 30% | PAUSE |
| Otherwise | CONTINUE |

---

## Database Schema

```
portfolios
  ├── portfolio_missions      (M2M: Portfolio ↔ Mission)
  ├── portfolio_resources     (Resource pools per portfolio)
  ├── portfolio_constraints   (Hard/soft constraint tracking)
  ├── portfolio_allocations   (Immutable per-mission resource records)
  ├── portfolio_evaluations   (Health snapshots)
  ├── portfolio_decisions     (Decision lifecycle)
  ├── portfolio_versions      (Immutable version history)
  └── portfolio_checkpoints   (Checkpoint decisions)
```

All tables: `organization_id NOT NULL` · `created_at` · `updated_at`  
Indexes: `organization_id`, `status`, `portfolio_id`, `created_at`

---

## Integration Map

| System | Integration |
|---|---|
| v2.4 Missions | FK `portfolio_missions.mission_id → missions.id`; `MissionEvaluationEngine` read |
| v2.0 Strategy | FK `portfolios.objective_id → strategic_objectives.id` |
| v1.6 GovernanceService | `create_approval_request()` on high-risk rebalancing |
| v2.2 ForecastingEngine | `TrendAnalysisEngine` reused for scenario simulation |
| v2.3 CommandCenter | `ExecutiveHealthEngine` accepts optional `portfolio_score` |
| EventPublisher | 18 `portfolio.*` SSE events across all lifecycle transitions |

---

## API Reference

```
GET  /api/v1/portfolio/overview
POST /api/v1/portfolio/portfolios
GET  /api/v1/portfolio/portfolios
GET  /api/v1/portfolio/portfolios/{id}
GET  /api/v1/portfolio/portfolios/{id}/missions
GET  /api/v1/portfolio/portfolios/{id}/resources
GET  /api/v1/portfolio/portfolios/{id}/risk
GET  /api/v1/portfolio/portfolios/{id}/explanation
GET  /api/v1/portfolio/portfolios/{id}/versions
POST /api/v1/portfolio/portfolios/{id}/evaluate
POST /api/v1/portfolio/portfolios/{id}/optimize
POST /api/v1/portfolio/portfolios/{id}/simulate
POST /api/v1/portfolio/portfolios/{id}/rebalance
POST /api/v1/portfolio/portfolios/{id}/checkpoint
POST /api/v1/portfolio/portfolios/{id}/approve
```

All endpoints: JWT authenticated · RBAC protected · organization isolated.

---

## Security

- All routes require `Depends(get_current_user)`
- `organization_id` extracted from JWT and enforced on every DB query
- No cross-tenant FK references possible
- `GovernanceService.create_approval_request()` called for all high-risk decisions
- No secrets in API responses, logs, or SSE payloads

---

## SSE Events

```
portfolio.created
portfolio.ready
portfolio.evaluating
portfolio.priority.updated
portfolio.resource.allocated
portfolio.resource.rebalanced
portfolio.constraint.detected
portfolio.risk.updated
portfolio.governance.pending
portfolio.governance.approved
portfolio.rebalancing
portfolio.mission.selected
portfolio.mission.deferred
portfolio.mission.paused
portfolio.checkpoint
portfolio.completed
portfolio.failed
```
