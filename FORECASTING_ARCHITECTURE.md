# FORECASTING ARCHITECTURE — STRTOS v2.2.0

## Strategic Forecasting, Future-State Simulation & Proactive Decision Intelligence

StrtOS v2.2.0 upgrades the system from observing current business state to forecasting possible future business states, simulating strategic scenarios, and preparing governed decisions before outcomes occur.

### Pipeline Architecture

```
CURRENT BUSINESS STATE
        ↓
HISTORICAL MEMORY & KNOWLEDGE GRAPH
        ↓
TREND ANALYSIS (Upward, Downward, Stable, Volatile)
        ↓
MULTI-HORIZON FORECAST (7, 14, 30, 60, 90, 180, 365 Days)
        ↓
SIDE-EFFECT FREE WHAT-IF SIMULATOR
        ↓
FUTURE RISK & OPPORTUNITY RADAR
        ↓
PREPARED ACTION PLANS
        ↓
GOVERNANCE EVALUATION
        ↓
ACTUAL OUTCOME MEASUREMENT
        ↓
ACCURACY & CALIBRATION (Overconfident, Underconfident, Well-Calibrated)
        ↺
```

### Core Components
1. **Forecasting Domain** (`backend/app/forecasting/models.py`, `schemas.py`, `repository.py`):
   * Forecast Types: `BUSINESS_HEALTH`, `REVENUE`, `CUSTOMER_GROWTH`, `CONVERSION`, `SEO`, `STRATEGIC_OBJECTIVE`.
   * Statuses: `DRAFT`, `GENERATED`, `ACTIVE`, `DEGRADED`, `EXPIRED`, `MEASURED`.
   * Enforces strict multi-tenant `organization_id` isolation.
2. **Strategic Forecasting & Trend Engines** (`backend/app/forecasting/engine.py`):
   * `TrendAnalysisEngine`: Computes trend direction, strength, change rate, and acceleration.
   * `StrategicForecastEngine`: Multi-horizon metric bounds with horizon-decaying confidence scores.
   * `FutureStateSimulationEngine`: Side-effect free what-if simulator allowing budget and intensity parameter adjustments.
   * `FutureRiskEngine` & `FutureOpportunityEngine`: Proactively identifies future revenue decline, campaign failures, and growth catalysts.
   * `ForecastAccuracyEngine`: Measures absolute error and calibration status (`WELL_CALIBRATED`, `OVERCONFIDENT`, `UNDERCONFIDENT`).
3. **REST API** (`backend/app/forecasting/routes.py` & `main.py`):
   * Mounted `/api/v1/forecasting` endpoints for forecast CRUD, simulation, future risk/opportunity discovery, and accuracy measurement.
4. **Strategic Forecasting Control Center UI** (`src/pages/ForecastingPage.tsx`, `src/services/forecastingApi.ts`):
   * Interactive multi-horizon trend selector, what-if simulator slider, future risk radar, and opportunity preparation cards.
