# Competitor Research Agent - StrtOS

The **Competitor Research Agent** is the third specialist AI agent in StrtOS. It identifies direct and indirect industry rivals, benchmarks pricing tiers, evaluates competitor digital presence and search share, discovers market gaps, and builds competitive positioning matrices.

## Responsibilities

- **Rival Discovery**: Identifies direct and indirect market competitors.
- **Pricing & Share Benchmarking**: Compares pricing tiers, digital presence scores, and market share estimates.
- **Market Gap Identification**: Isolates unfulfilled customer pain points (e.g. slow response times, static promotional codes).
- **Strength & Weakness Matrix**: Maps competitors across core operational metrics.
- **CEO Agent Delegation**: Receives delegated tasks ONLY from the CEO Agent Orchestrator via `SpecialistAgentInterface`.

## Module Architecture

```
backend/app/agents/competitor_research/
├── competitor_agent.py  # Main Agent entry point
├── models.py            # Async SQLAlchemy 2.0 Database Persistence Model
├── schemas.py           # Pydantic v2 Input/Output DTO schemas
├── prompts.py           # Strict system prompt for competitor research
├── tools.py             # Tool suite abstractions (Discovery, Google, Website, Social, SEO, Pricing, Gap)
├── service.py           # Core Competitor Research service & Redis event transport
├── validator.py         # Input validator & JSON output schema validator
├── interfaces.py        # Wrapper implementing SpecialistAgentInterface
└── README.md            # Module technical documentation
```
