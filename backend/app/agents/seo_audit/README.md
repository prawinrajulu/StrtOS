# SEO Audit Agent - StrtOS

The **SEO Audit Agent** is the second specialist AI agent in StrtOS. It evaluates technical web architecture, DOM structures, page speed metrics, Core Web Vitals, HTML heading hierarchy, meta tags, schema markup, and crawlability.

## Responsibilities

- **Technical SEO Audit**: Evaluates crawlability, indexation health, and robots.txt / sitemap.xml.
- **Core Web Vitals**: Measures LCP, FID, and CLS scores.
- **On-Page Optimization**: Audits H1/H2 tags, title tags, meta descriptions, and image ALT attributes.
- **Issue Classification**: Categorizes findings into Critical Issues, Warnings, and Priority Fixes.
- **CEO Agent Delegation**: Receives delegated tasks ONLY from the CEO Agent Orchestrator via `SpecialistAgentInterface`.

## Module Architecture

```
backend/app/agents/seo_audit/
├── seo_agent.py        # Main Agent entry point
├── models.py           # Async SQLAlchemy 2.0 Database Model
├── schemas.py          # Pydantic v2 Input/Output DTO schemas
├── prompts.py          # Strict system prompt for technical SEO
├── tools.py            # Tool suite abstractions (Crawler, PageSpeed, Robots, Sitemap, Schema, Vitals)
├── service.py          # Core SEO Audit service & Redis event transport
├── validator.py        # URL HTTPS validator & JSON output schema validator
├── interfaces.py       # Wrapper implementing SpecialistAgentInterface
└── README.md
```
