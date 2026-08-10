# StrtOS v1.2.0 — Predictive Decision Intelligence & Scenario Simulation Architecture

## Overview
StrtOS v1.2.0 introduces **Predictive Decision Intelligence & Scenario Simulation**. This system combines verified current evidence, historical memory, previous actual outcome variances, client goals, budget constraints, and risk limits to generate deterministic decision scenarios (`CONSERVATIVE`, `BALANCED`, `AGGRESSIVE`, `CUSTOM`) with predicted value ranges, confidence scores, and risk levels.

---

## Predictive Architecture Diagram

```
                        +-----------------------------------+
                        |    StrtOS REST API & Event Bus    |
                        |   - /api/v1/predictions           |
                        |   - /api/v1/predictions/scenarios |
                        |   - /api/v1/predictions/simulate  |
                        +-----------------+-----------------+
                                          |
                                          v
                        +-----------------------------------+
                        |    Prediction Service Layer       |
                        |    (Multi-Tenant Isolation)       |
                        +--------+-----------------+--------+
                                 |                 |
            +--------------------+                 +--------------------+
            |                                                           |
            v                                                           v
+-----------------------------------+                       +-----------------------------------+
|     Scenario Engine & Range       |                       |    What-If Decision Simulator     |
|  - CONSERVATIVE (Lower exposure)  |                       |  - Current vs Simulated Budget    |
|  - BALANCED (Standard flight)     |                       |  - Diminishing returns model      |
|  - AGGRESSIVE (High scaling)      |                       |  - Delta & Risk Evaluation        |
+-----------------+-----------------+                       +-----------------+-----------------+
                  |                                                           |
                  v                                                           v
+-----------------------------------------------------------------------------------------------+
|                                Live Supabase PostgreSQL DB                                    |
|                                - predictions table (33 columns, 7 indexes)                   |
+-----------------------------------------------------------------------------------------------+
```

---

## Mandatory Transparency Rules
Predictions are **NOT** evidence. The system strictly demarcates and presents:
1. `CURRENT VERIFIED EVIDENCE`
2. `HISTORICAL MEMORY (DO NOT CITE AS CURRENT EXTERNAL SOURCE)`
3. `PREDICTION RANGE`
4. `AI ASSUMPTIONS & CONSTRAINTS`

---

## Key Architecture Components

1. **Database Schema (`PredictionModel`)**:
   - Mapped to `predictions` table in live Supabase PostgreSQL.
   - Enums: `ScenarioType` (`CONSERVATIVE`, `BALANCED`, `AGGRESSIVE`, `CUSTOM`) and `PredictionStatus`.
   - Indexed on `organization_id`, `client_id`, `workflow_id`, `scenario_type`, `prediction_status`, and `created_at`.

2. **Scenario Engine (`scenario_engine.py`)**:
   - Generates deterministic scenarios with explicit upper/lower bounds, confidence scores, risk scores, and assumptions.

3. **Accuracy Engine (`accuracy.py`)**:
   - Compares predicted values against actual outcomes (`HIGH_ACCURACY` <=10% error, `MODERATE_ACCURACY` <=25% error, `CALIBRATION_REQUIRED` >25% error).

4. **Governance Integration**:
   - Submitting high-risk scenario selections triggers Governance `ApprovalRequest` workflows.

5. **Real-Time SSE Events**:
   - Publishes `prediction.created`, `prediction.scenario.created`, `prediction.simulation.completed`, `prediction.approval.pending`, and `prediction.approved`.
