# StrtOS - Autonomous Multi-Agent AI Operating System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-v0.1.0--alpha-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**StrtOS** is an autonomous Multi-Agent AI Operating System designed to decompose high-level executive business directives into coordinated multi-stage execution graphs across specialized AI agents.

```
                               ┌────────────────────────┐
                               │  Executive Directive   │
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

- **CEO Orchestration Engine**: Intent analysis, decision evaluation, task planning, confidence scoring, and executive report synthesis.
- **5 Implemented Specialist Agents**:
  - `Business Analysis Agent`: TAM benchmark analysis, SWOT matrix, digital/business maturity scoring, customer personas.
  - `SEO Audit Agent`: Crawlability, Core Web Vitals, HTML heading hierarchy, meta tags, schema validation.
  - `Competitor Research Agent`: Rival mapping, pricing benchmarking, digital presence scoring, market gap analysis.
  - `Marketing Strategy Agent`: Brand positioning, UVP, multi-channel budget allocation, funnel design, 90-day growth roadmaps.
  - `Campaign Planner Agent`: Flighting schedules, creative asset requirements, weekly roadmaps, pre-launch checklists.
- **Real-Time Event Stream**: Redis Pub/Sub integration feeding live thought streams and task progress via Server-Sent Events (SSE).
- **React Flow UI Integration**: Pixel-perfect dark-mode visualizer with glowing active execution nodes, green completed nodes, and animated edges.

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
