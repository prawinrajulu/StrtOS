# Business Analysis Agent - StrtOS

The **Business Analysis Agent** is the first specialist AI agent in StrtOS. It evaluates business viability, industry positioning, SWOT analysis, digital/business maturity scores, customer personas, business risks, and strategic growth opportunities.

## Responsibilities

- **SWOT Analysis**: Generates Strengths, Weaknesses, Opportunities, and Threats.
- **Customer Personas**: Identifies buyer demographics, pain points, and motivations.
- **Maturity Scores**: Computes digital maturity score (0-100) and business maturity score (0-100).
- **Growth Opportunities & Risks**: Outlines high-impact expansion drivers and risk factors.
- **CEO Agent Delegation**: Receives delegated tasks ONLY from the CEO Agent Orchestrator via `SpecialistAgentInterface`.

## Module Architecture

```
backend/app/agents/business_analysis/
├── business_agent.py    # Main Agent entry point
├── models.py            # SQLAlchemy 2.0 Database Persistence Model
├── schemas.py           # Pydantic v2 Input/Output validation schemas
├── prompts.py           # System prompts with strict boundary constraints
├── tools.py             # External tool abstractions (Website, Google, Financials)
├── service.py           # Core Business Analysis evaluation service & Redis events
├── validator.py         # Input & JSON schema output validator
├── interfaces.py        # Wrapper implementing SpecialistAgentInterface
└── README.md
```
