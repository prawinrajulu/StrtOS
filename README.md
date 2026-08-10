# StrtOS - Autonomous Multi-Agent AI Operating System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-v1.3.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**StrtOS** is an autonomous Multi-Agent AI Operating System designed to decompose high-level executive business directives into coordinated multi-stage execution graphs across specialized AI agents.

> **Security Guarantee**: LLM outputs are proposals, never direct executable commands. All execution passes through an explicit `ActionRegistry`, deterministic `PolicyEngine`, and `Governance` human approval layer.

```
                                ┌────────────────────────┐
                                │  Executive Directive   │
                                └───────────┬────────────┘
                                            │
                                            ▼
                                ┌────────────────────────┐
                                │ Predictive Engine &    │
                                │ Scenario Simulator     │
                                └───────────┬────────────┘
                                            │
                                            ▼
                                ┌────────────────────────┐
                                │   Memory Retrieval     │
                                │(Deterministic Ranker)  │
                                └───────────┬────────────┘
                                            │
                                            ▼
                                ┌────────────────────────┐
                                │ Human Governance Layer │
                                │(Deterministic Risk Eng)│
                                └───────────┬────────────┘
                                            │
                                            ▼
                                ┌────────────────────────┐
                                │ Policy Engine & Action │
                                │ Execution Control Loop │
                                └───────────┬────────────┘
                                            │
                                            ▼
                                ┌────────────────────────┐
                                │   CEO Agent Engine     │
                                │(LangGraph Orchestrator)│
                                └───────────┬────────────┘
                                            │
          ┌──────────────────┬──────────────┼──────────────┬──────────────────┐
          │                  │              │              │                  │
          ▼                  ▼              ▼              ▼                  ▼
 ┌─────────────────┐ ┌──────────────┐ ┌───────────┐ ┌─────────────┐ ┌──────────────────┐
 │Business Analysis│ │  SEO Audit   │ │Competitor │ │ Marketing   │ │ Campaign Planner │
 │     Agent       │ │    Agent     │ │ Research  │ │ Strategy    │ │      Agent       │
 └─────────────────┘ └──────────────┘ └───────────┘ └─────────────┘ └──────────────────┘
```

---

## Key Features

- **Autonomous Execution & Closed-Loop Optimization (v1.3.0)**:
  - `ActionModel` with multi-tenant isolation, 26 columns, 10 indexes, and foreign keys to live Supabase PostgreSQL.
  - **Action Registry Allowlist**: Strict registry of safe executable actions (`GENERATE_REPORT`, `RUN_SEO_AUDIT`, `RUN_WEBSITE_AUDIT`, etc.), strictly blocking arbitrary shell, SQL, Python eval, or credential access.
  - **Deterministic Policy Engine**: Evaluates role RBAC, multi-tenancy, risk level rules, autonomy modes (`MANUAL`, `ASSISTED`, `APPROVAL_REQUIRED`, `AUTONOMOUS`), and governance approval states.
  - **Action Executor & Idempotency**: Manages tool execution, state machine transitions, retry handling, and idempotency key deduplication.
  - **Closed-Loop Optimization Engine**: Evaluates actual execution KPI telemetry against predictions, calculates accuracy scores, maps outcome status, and records grounded lessons to v1.1 Memory.
  - **Execution UI (`ExecutionPage.tsx`, `ActionDetailsPage.tsx`)**: Dark-glass control panel with real-time SSE stream auto-refresh.

- **Predictive Decision Intelligence & Scenario Simulation (v1.2.0)**:
  - `PredictionModel` with multi-tenant isolation, 33 columns, 7 indexes, and foreign keys to live Supabase PostgreSQL.
  - **Scenario Engine**: Deterministic generation of `CONSERVATIVE`, `BALANCED`, and `AGGRESSIVE` decision scenarios.
  - **What-If Decision Simulator**: Interactive budget simulation with expected metric ranges and delta calculations.
  - **Prediction Accuracy Engine**: Evaluates prediction accuracy against v1.1 actual performance outcomes.
  - **Predictions UI (`PredictionsPage.tsx`, `PredictionSimulatorPage.tsx`)**: Dark-glass control panel with real-time SSE stream auto-refresh.
- **Adaptive Intelligence & Memory Layer (v1.1.0)**:
  - `MemoryRecordModel` with multi-tenant isolation, 8 memory types (`CLIENT_CONTEXT`, `DECISION`, `STRATEGY`, `APPROVAL`, `WORKFLOW`, `OUTCOME`, `FEEDBACK`, `LESSON`), and foreign keys to live Supabase PostgreSQL.
  - **Deterministic Memory Retrieval Engine**: Scores candidate memories based on Client Match, Industry Match, Keyword Overlap, Recency, Importance/Confidence, and Outcome status.
  - **Outcome Variance Evaluator**: Compares AI PREDICTED KPI vs ACTUAL KPI values (`SUCCESS` <=10%, `PARTIAL` 10-30%, `FAILED` >30%).
  - **Grounded Lesson Extractor**: Derives non-fabricated learned signals from stored outcome data.
  - **Memory UI (`MemoryPage.tsx`, `OutcomesPage.tsx`)**: Dark-glass control panels with real-time SSE stream auto-refresh.
- **Human Approval & AI Decision Governance Layer (v1.0.0)**:
  - `ApprovalRequestModel` with multi-tenant isolation, state machine transitions, and foreign keys to live Supabase PostgreSQL.
  - **Deterministic Risk Engine**: 0–100 scoring algorithm classifying decisions into `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL` risk tiers.
  - **Self-Approval Prevention**: Service-level enforcement forbidding requestors from approving their own governance requests.
  - **Workflow Engine Integration**: Pauses high-risk or governance-flagged workflows until explicit reviewer approval.
  - **Governance UI (`ApprovalsPage.tsx`)**: Dark-glass control panel with real-time SSE stream auto-refresh.
- **CEO Orchestration Engine**: Intent analysis, decision evaluation, task planning, confidence scoring, and executive report synthesis.
- **Evidence-Based Specialist Intelligence (v0.9.0)**:
  - `EvidenceItem` contract: Standardized provenance tracking across `website`, `search`, `api`, `database`, `llm`, `assumption`, `unavailable`.
  - **Deterministic Confidence Engine**: Weighted scoring algorithm prioritizing direct API/Database verification > Website > Search > LLM inference.
- **5 Specialist AI Agents**:
  - `Business Analysis Agent`: TAM benchmark analysis, SWOT matrix, digital/business maturity scoring, customer personas.
  - `SEO Audit Agent`: Crawlability, Core Web Vitals, HTML heading hierarchy, meta tags, schema validation.
  - `Competitor Research Agent`: Rival mapping, pricing benchmarking, digital presence scoring, market gap analysis.
  - `Marketing Strategy Agent`: Brand positioning, UVP, multi-channel budget allocation, funnel design, 90-day growth roadmaps.
  - `Campaign Planner Agent`: Flighting schedules, creative asset requirements, weekly roadmaps, pre-launch checklists.
- **Real-Time Event Stream**: Typed real-time events (`approval.created`, `approval.pending`, `approval.approved`, `approval.rejected`, `agent.started`, `agent.completed`) broadcast over Redis Pub/Sub & SSE.
- **React Flow UI Integration**: Dark-glass visualizer with glowing execution nodes, confidence badges, evidence counters, and telemetry metrics.

---

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, Async SQLAlchemy 2.0, PostgreSQL 16, Redis 7 Pub/Sub, LangGraph.
- **Frontend**: React 19, TypeScript, Vite, `@xyflow/react` (React Flow), Lucide React.
- **DevOps**: Docker & Docker Compose.

---

## Folder Structure

```
StrtOS/
├── backend/
│   ├── alembic/                 # Database migrations
│   ├── app/
│   │   ├── api/v1/              # API Routers (auth, ceo, clients, dashboard, etc.)
│   │   ├── core/                # Config, DB async engine, Redis Pub/Sub, security
│   │   ├── models/              # SQLAlchemy 2.0 DB models
│   │   ├── schemas/             # Pydantic v2 DTO schemas
│   │   ├── repositories/        # Async Repository Pattern
│   │   ├── services/            # Service layer (AuthService, etc.)
│   │   └── agents/              # Specialist & CEO Agent modules
│   │       ├── ceo/             # CEO Agent Orchestrator & LangGraph state
│   │       ├── business_analysis/
│   │       ├── seo_audit/
│   │       ├── competitor_research/
│   │       ├── marketing_strategy/
│   │       └── campaign_planner/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/                         # React 19 TypeScript Frontend
│   ├── components/              # Reusable React components & React Flow graph
│   ├── pages/                   # AI Agents, CEO Agent, Dashboard pages
│   └── services/                # API & SSE Stream Client
├── docs/                        # Architecture & Engineering docs
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── SECURITY.md
```

---

## Getting Started

### Using Docker Compose

```bash
cd backend
docker-compose up -d --build
```

### Manual Development Setup

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   npm install
   npm run dev
   ```

Access the API Documentation at `http://localhost:8000/docs` and the Dashboard at `http://localhost:5173`.

---

## License

This project is licensed under the [MIT License](LICENSE).
