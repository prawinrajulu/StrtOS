# StrtOS v2.7.0 — Autonomous Strategic Portfolio Optimization & Capital Allocation Architecture

## Overview

StrtOS v2.7.0 introduces the **Autonomous Strategic Portfolio Optimization & Capital Allocation Layer**, operating directly above Strategy, Missions, and Resource Intelligence.

It enables StrtOS to answer four core strategic questions:
1. **WHICH STRATEGIC INITIATIVES SHOULD STRtOS PRIORITIZE?**
2. **WHERE SHOULD LIMITED RESOURCES BE ALLOCATED?**
3. **WHAT SHOULD BE DELAYED, REDUCED, OR STOPPED?**
4. **WHAT IS THE EXPECTED BUSINESS VALUE OF THE CURRENT PORTFOLIO?**

---

## Operating Loop Extension

```
REAL DATA → STRATEGY → DECISION → PORTFOLIO OPTIMIZATION → INITIATIVE PRIORITIZATION → CAPITAL ALLOCATION → GOVERNANCE → EXECUTION → LEARNING
```

---

## Key Components

### 1. Data Models (`backend/app/portfolio/models.py`)
- `StrategicPortfolioModel`: Root multi-tenant portfolio table (`portfolios`).
- `PortfolioInitiativeModel`: Initiative-level objectives (`portfolio_initiatives`).
- `PortfolioRecommendationModel`: Action recommendations (`portfolio_recommendations`).
- `PortfolioMissionModel`, `PortfolioResourceModel`, `PortfolioConstraintModel`, `PortfolioAllocationModel`, `PortfolioEvaluationModel`, `PortfolioDecisionModel`, `PortfolioVersionModel`, `PortfolioCheckpointModel`.
- All tables enforce strict non-nullable `organization_id` foreign key & index for multi-tenant security.

### 2. Analytical & Optimization Engines (`backend/app/portfolio/engine.py` & `optimizer.py`)
- **`PortfolioOptimizationEngine`**: Greedy knapsack optimizer supporting `CONSERVATIVE`, `BALANCED`, `AGGRESSIVE`, and `CUSTOM` scenarios.
- **`CapitalAllocationEngine`**: Deterministic budget & capital allocation return. Returns `INSUFFICIENT_DATA` when financial telemetry is unconfigured or zero.
- **`PortfolioTradeoffEngine`**: Evaluates explicit trade-offs ("What happens if Initiative A is prioritized over Initiative B?").
- **`DoNothingSimulationEngine`**: Compares `CURRENT PORTFOLIO` vs `OPTIMIZED PORTFOLIO` vs `DO NOTHING` baseline degradation (side-effect free).
- **`PortfolioRecommendationEngine`**: Classifies recommendations into `CONTINUE`, `ACCELERATE`, `MAINTAIN`, `DELAY`, `REDUCE`, `STOP`, `REVIEW`. `STOP` requires high risk (>= 75), zero/negative expected value, or persistent failure. High-risk actions set `requires_governance = True`.

### 3. Service & Integrations (`backend/app/portfolio/service.py`)
- Integrated with `GovernanceService` for human approval routing on `STOP` or high-risk recommendations.
- Integrated with `PolicyEngine` for active restriction checks (`POLICY_BLOCKED`).
- Integrated with `MemoryService` for portfolio decision memory records.
- Integrated with `KnowledgeService` for causal knowledge graph mapping (Objective → Initiative → Mission → Resource → Execution → Outcome).
- SSE Event Notifications: `portfolio.updated`, `portfolio.optimized`, `portfolio.recommendation.created`, `portfolio.simulation.completed`, `portfolio.risk.detected`, `portfolio.governance.pending`, `portfolio.allocation.updated`.

### 4. REST API Contract (`backend/app/portfolio/routes.py`)
- `GET /api/v1/portfolio/overview`
- `GET /api/v1/portfolio/initiatives`, `POST /api/v1/portfolio/initiatives`, `GET /api/v1/portfolio/initiatives/{id}`
- `POST /api/v1/portfolio/optimize`
- `GET /api/v1/portfolio/recommendations`, `GET /api/v1/portfolio/recommendations/{id}`
- `POST /api/v1/portfolio/simulate`
- `POST /api/v1/portfolio/evaluate`
- `GET /api/v1/portfolio/tradeoffs`
- `GET /api/v1/portfolio/allocations`, `POST /api/v1/portfolio/allocations/simulate`
- `GET /api/v1/portfolio/explanation/{id}`
- `POST /api/v1/portfolio/recommendations/{id}/governance`

### 5. Frontend UI/UX (`src/pages/`)
- **Invisible AI Architecture**: No AI agent or swarm names exposed in normal UI views.
- Sub-tab navigation in `PortfolioPage.tsx`:
  - `PortfolioControlCenterPage.tsx`: Strategic Portfolio Score (0-100), Health, EV, Spend, Initiative Prioritization table, Capital Allocation breakdown, system recommendations.
  - `PortfolioSimulationPage.tsx`: What-If scenario simulator, Do-Nothing vs Optimized comparison, budget & capacity sliders, trade-off pair evaluation cards.
  - `PortfolioRecommendationsPage.tsx`: Actionable recommendations with Governance routing buttons.
  - `PortfolioDetailsPage.tsx`: Detailed causal knowledge explanation chain & version history.

---

## Verification & Compliance

- **Backend Pytest Suite**: 255 passed / 0 failed.
- **Frontend Production Build**: `npm run build` completed successfully (2039 modules transformed).
- **Security Audit**: Multi-tenant isolation verified (`organization_id` required across all endpoints & tables).
- **Backward Compatibility**: Fully backward compatible with StrtOS v1.0–v2.6.0.
