# Marketing Strategy Agent - StrtOS

The **Marketing Strategy Agent** is the fourth specialist AI agent in StrtOS. It synthesizes upstream findings from the Business Analysis, SEO Audit, and Competitor Research Agents into a practical digital marketing strategy.

## Responsibilities

- **Brand Positioning & UVP**: Synthesizes unique value propositions and brand positioning statement.
- **Channel Allocation**: Recommends digital acquisition channels (Search Ads, Social Video, Retargeting/Email) with budget percentages.
- **Customer Journey & Funnel**: Defines TOFU, MOFU, and BOFU funnel conversion stages.
- **90-Day Growth Roadmap**: Outlines phased 30/60/90 day execution tactics.
- **CEO Agent Delegation**: Receives delegated tasks ONLY from the CEO Agent Orchestrator via `SpecialistAgentInterface`.

## Module Architecture

```
backend/app/agents/marketing_strategy/
├── marketing_agent.py   # Main Agent entry point
├── models.py            # Async SQLAlchemy 2.0 Database Persistence Model
├── schemas.py           # Pydantic v2 Input/Output DTO schemas
├── prompts.py           # Strict system prompt for marketing strategy
├── tools.py             # Tool suite abstractions (Audience, Channel, Budget, Persona, Content, Benchmark, Forecast)
├── service.py           # Core Marketing Strategy service & Redis event transport
├── validator.py         # Upstream inputs & JSON output schema validator
├── interfaces.py        # Wrapper implementing SpecialistAgentInterface
└── README.md            # Module technical documentation
```
