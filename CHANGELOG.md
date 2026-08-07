# Changelog

All notable changes to the StrtOS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0-alpha] - 2026-08-07

### Added
- **FastAPI Backend Foundation**: Async SQLAlchemy 2.0 connection pool, Redis Pub/Sub manager, correlation tracking middleware (`X-Request-ID`), JWT bearer security, and Pydantic v2 schemas.
- **CEO Agent Orchestrator**: Intent Engine, Decision Engine, Workflow Planner, Task Planner, Execution Monitor, Validator, Confidence Calculator, and Executive Reporter.
- **5 Specialist AI Agents**:
  - `Business Analysis Agent`: TAM benchmark analysis, SWOT matrix, digital/business maturity scores, customer personas.
  - `SEO Audit Agent`: Crawlability, Core Web Vitals, HTML heading hierarchy, meta tags, schema validation.
  - `Competitor Research Agent`: Rival mapping, pricing benchmarking, digital presence scoring, market gap analysis.
  - `Marketing Strategy Agent`: Brand positioning, UVP, multi-channel budget allocation, funnel design, 90-day growth roadmaps.
  - `Campaign Planner Agent`: Flighting schedules, creative asset requirements, weekly roadmaps, pre-launch checklists.
- **React Flow Visualizer**: Animated graph rendering active execution nodes, pulsing edges, completed green nodes, and real-time SSE event stream.

### Changed
- Standardized specialist interfaces via `SpecialistAgentInterface` contract to eliminate circular imports.

### Fixed
- Fixed TypeScript type imports for `verbatimModuleSyntax` compatibility in Vite build pipeline.

### Known Issues
- Tool abstractions currently run local benchmark simulations; external API integrations (Google Search, PageSpeed Insights, SEMrush) will be connected in Phase 2.

### Next Release Goals (v0.2.0-beta)
- Implement `Content Strategy Agent`, `Opportunity Intelligence Agent`, and `Analytics Agent`.
- Integrate LLM API bindings (Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o).
