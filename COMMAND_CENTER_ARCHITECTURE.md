# COMMAND CENTER ARCHITECTURE — STRTOS v2.3.0

## Autonomous Strategic Command Center & Decision Cockpit

StrtOS v2.3.0 unifies all 17 AI intelligence subsystems (Evidence, Memory, Knowledge Graph, Causal Intelligence, Predictions, Business State, Early Warnings, Forecasting, Swarm, Agent Intelligence, Strategy, Decision Optimization, Governance, Execution, Outcome, Learning, Policy Evolution) into a single unified Executive Command Center.

### Unified Decision Pipeline Architecture

```
OBSERVE (Real Data → Business State Telemetry)
    ↓
UNDERSTAND (Evidence → Memory → Knowledge Graph → Causal Factors)
    ↓
FORECAST (Trend Analysis → Multi-Horizon Scenarios → Future Risk/Opportunity)
    ↓
DEBATE (5 Specialist Agent Swarm Consensus & Dissent Analysis)
    ↓
DECIDE (Side-Effect Free 'Do Nothing' Trajectory vs Recommended Action)
    ↓
GOVERN (GovernanceService Rules & Autonomy Level Classification)
    ↓
EXECUTE (Governed Action Plans via ExecutionEngine & ActionRegistry)
    ↓
MEASURE (Outcome Variance & Prediction Accuracy)
    ↓
LEARN (Agent Performance, Policy Evolution & Bounded Strategy Adaptation)
    ↺
```

### Core Components
1. **Command Center Read-Model Domain** (`backend/app/command_center/models.py`, `schemas.py`, `repository.py`):
   * Orchestration layer aggregating existing subsystems without duplicating domain source of truth.
   * Enforces strict multi-tenant `organization_id` isolation.
2. **Executive & Strategic Engines** (`backend/app/command_center/engine.py`):
   * `ExecutiveHealthEngine`: Deterministically calculates scores across 7 operational subsystems (`EXCELLENT`, `HEALTHY`, `WATCH`, `AT_RISK`, `CRITICAL`).
   * `StrategicPriorityEngine`: Ranks business issues by severity and financial exposure (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
   * `DoNothingSimulationEngine`: Side-effect free simulation calculating expected trajectory if no action is taken.
   * `AutonomyStatusEngine`: Classifies decision autonomy level (`MANUAL`, `ASSISTED`, `APPROVAL_REQUIRED`, `AUTONOMOUS`).
3. **REST API** (`backend/app/command_center/routes.py` & `main.py`):
   * Mounted `/api/v1/command-center` endpoints for overview, health, priorities, decisions, alternatives, explanations, and agent consensus.
4. **AI Operations Cockpit UI** (`src/pages/CommandCenterPage.tsx`, `src/services/commandCenterApi.ts`):
   * Executive Health Strip, Strategic Priorities, Decision Cockpit, and 5 Specialist Agent Consensus Panel.
