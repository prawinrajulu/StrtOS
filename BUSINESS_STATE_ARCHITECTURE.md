# BUSINESS STATE ARCHITECTURE — STRTOS v2.1.0

## Continuous Business State Intelligence & Strategic Early-Warning Layer

StrtOS v2.1.0 introduces real-time business telemetry, metric change detection, and proactive strategic early warnings.

### Architecture Pipeline

```
REAL DATA
   ↓
BUSINESS STATE NORMALIZATION
   ↓
BASELINE COMPARISON & CHANGE DETECTION
   ↓
ANOMALY DETECTION & METRIC SIGNALS
   ↓
OPPORTUNITY / THREAT DISCOVERY
   ↓
CAUSAL IMPACT ANALYSIS
   ↓
STRATEGIC EARLY-WARNING ALERTS
   ↓
DECISION OPTIMIZATION & GOVERNANCE EVALUATION
   ↓
GOVERNED STRATEGIC RESPONSE / ACTION PLAN
   ↓
ACTUAL OUTCOME MEASUREMENT
   ↺
```

### Core Components
1. **Business State Domain** (`backend/app/business_state/models.py`, `schemas.py`, `repository.py`):
   * Snapshots (`CURRENT`, `BASELINE`, `HISTORICAL`).
   * Alert lifecycle: `DETECTED`, `ACKNOWLEDGED`, `INVESTIGATING`, `ACTION_RECOMMENDED`, `GOVERNANCE_PENDING`, `RESOLVED`, `DISMISSED`.
   * Enforces strict multi-tenant `organization_id` isolation.
2. **Baseline & Change Detection Engine** (`backend/app/business_state/engine.py`):
   * Computes absolute & percentage deltas, direction (`INCREASE`, `DECREASE`, `STABLE`, `UNKNOWN`), and severity (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
3. **Opportunity & Threat Detectors**:
   * Scans metrics and changes to identify evidence-backed SEO tailwinds, funnel optimization advantages, and conversion deterioration threats.
4. **Deterministic Business Health Engine**:
   * Computes 0–100 health score (`EXCELLENT`, `HEALTHY`, `WATCH`, `AT_RISK`, `CRITICAL`).
5. **Continuous Business State Control Center UI** (`src/pages/BusinessStatePage.tsx`, `src/services/businessStateApi.ts`):
   * Provides active early-warning telemetry, opportunity/threat split views, and interactive alert resolution workflows.
