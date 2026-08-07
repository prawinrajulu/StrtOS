# Campaign Planner Agent - StrtOS

The **Campaign Planner Agent** is the fifth specialist AI agent in StrtOS. It converts upstream Marketing Strategy directions into concrete, channel-by-channel campaign flighting schedules, creative asset requirements, weekly execution roadmaps, and pre-launch checklists.

## Responsibilities

- **Execution Flighting Schedule**: Structures 90-day campaign rollout phases.
- **Creative Specifications**: Outlines video ad dimensions, ad copy requirements, and landing page load speed goals.
- **Weekly Roadmap**: Details week-by-week activities, focus themes, and target milestones.
- **Pre-Launch Checklist**: Generates pre-flight verification items (tag management, conversion tracking, spend caps).
- **CEO Agent Delegation**: Receives delegated tasks ONLY from the CEO Agent Orchestrator via `SpecialistAgentInterface`.

## Module Architecture

```
backend/app/agents/campaign_planner/
├── campaign_agent.py   # Main Agent entry point
├── models.py            # Async SQLAlchemy 2.0 Database Persistence Model
├── schemas.py           # Pydantic v2 Input/Output DTO schemas
├── prompts.py           # Strict system prompt for campaign planning
├── tools.py             # Tool suite abstractions (Scheduler, Budget, Creative, Calendar, Media, Optimization, Checklist)
├── service.py           # Core Campaign Planner service & Redis event transport
├── validator.py         # Strategy input & JSON output schema validator
├── interfaces.py        # Wrapper implementing SpecialistAgentInterface
└── README.md            # Module technical documentation
```
