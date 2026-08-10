# StrtOS v1.5.0 — Adaptive Agent Learning & Self-Optimization Architecture

## Overview
StrtOS v1.5.0 introduces **Adaptive Agent Learning & Self-Optimization**. This milestone upgrades StrtOS into a continuously improving AI Operating System that learns from verified historical outcomes, prediction accuracy telemetry, human governance decisions, and tool/provider performance metrics. Learning is strictly deterministic, bounded (max 10% delta), versioned (`agent_policies`), auditable, reversible (`PolicyRollbackEngine`), and multi-tenant isolated.

---

## Continuous Learning Control Loop Diagram

```
                       VERIFIED OUTCOME
                              │
                              ▼
                   PREDICTION ACCURACY
                              │
                              ▼
                  DETERMINISTIC RELIABILITY
                       SCORE ENGINE
                              │
                              ▼
                  BOUNDED ADAPTATION ENGINE
                     (Max 10% Delta)
                              │
                              ▼
                     GOVERNANCE APPROVAL
                       (If Delta > 5%)
                              │
                              ▼
                   VERSIONED AGENT POLICY
                      (AgentPolicyModel)
                              │
                              ▼
                   DEGRADATION MONITORING
                   (PolicyRollbackEngine)
                              │
                              ▼
                     BETTER FUTURE AGENT
                          EXECUTION
```

---

## Key Components

1. **Database Schema (5 Live Tables)**:
   - `agent_performance` (23 columns, 2 indexes)
   - `tool_reliability` (13 columns, 2 indexes)
   - `llm_provider_performance` (16 columns, 2 indexes)
   - `agent_policies` (12 columns, 3 indexes)
   - `agent_adaptations` (13 columns, 3 indexes)

2. **Deterministic Reliability Engine (`reliability_engine.py`)**:
   - Computes 0-100 reliability score using weighted formula:
     - Prediction Accuracy: 30%
     - Outcome Success Rate: 25%
     - Evidence Quality Score: 15%
     - Human Approval Rate: 10%
     - Tool Reliability: 10%
     - Swarm Consensus Rate: 5%
     - Execution Stability: 5%
   - Classifies: `EXCELLENT`, `GOOD`, `MODERATE`, `LOW`, `CRITICAL`, `INSUFFICIENT_DATA` (<3 executions).

3. **Bounded Adaptation Engine (`adaptation_engine.py`)**:
   - `MAX_ADAPTATION_DELTA = 10.0%`
   - High deltas (> 5%) route through Governance `ApprovalRequest`.
   - Creates grounded lessons in v1.1 Memory (`LESSON`, `FEEDBACK`, `OUTCOME`, `STRATEGY`).

4. **Versioned Policy & Rollback (`policy_engine.py`)**:
   - `AgentPolicyModel` tracks versioned configurations (`DRAFT`, `TESTING`, `ACTIVE`, `ROLLED_BACK`, `DEPRECATED`).
   - `PolicyRollbackEngine` automatically detects degradation (>15% drop in performance score, >20% drop in prediction accuracy) and executes tenant-isolated rollbacks to the prior active policy version.
