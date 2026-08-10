# StrtOS AI Intelligence & Evidence-Based Architecture

This document details the production AI intelligence architecture, evidence collection contract, confidence engine, real-tool integration, and real-time event streaming layer for StrtOS v0.9.0.

---

## 1. End-to-End Pipeline Architecture

```
CEO Directive / Workflow Start
      ↓
CEO Orchestrator
      ↓
Specialist Agent (Business, SEO, Competitor, Marketing, Campaign)
      ↓
Tool Registry (`execute_tool`) ─── Firecrawl / Tavily / Serper / PageSpeed / Google Business / Browser
      ↓
Evidence Collection (`EvidenceItem` - website | search | api | database | llm | assumption | unavailable)
      ↓
Confidence Engine (`calculate_confidence` - 0 to 100 deterministic scale)
      ↓
LLM Router (`route_and_generate`) ─── Gemini / Claude / OpenAI / DeepSeek / Qwen / OpenRouter
      ↓
Pydantic Validation & Output Verification
      ↓
CEO Synthesis & Executive Report Persistence
      ↓
Real-Time Event Stream (Redis Pub/Sub & SSE) ─── Frontend Dashboard UI
```

---

## 2. Evidence Contract (`EvidenceItem`)

Every claim or measurement produced during execution is stored as a structured `EvidenceItem`:

```json
{
  "finding": "Page load LCP is 1.1s",
  "source": "Tool:pagespeed",
  "source_type": "api",
  "url": "https://example.com",
  "evidence": {"performance_score": 90, "lcp": "1.1s"},
  "confidence": 100.0,
  "timestamp": "2026-08-10T14:10:00.000Z"
}
```

### Supported `source_type` Categories
1. `database` / `api`: Direct API or database verification (Weight: 1.0 / 0.95).
2. `website`: Scraped web content from Firecrawl or Browser (Weight: 0.85).
3. `search`: Web search benchmarks from Tavily or Serper (Weight: 0.70).
4. `llm`: Synthesized inference from LLM Router (Weight: 0.50).
5. `assumption`: Strategic benchmark or projection (Weight: 0.30).
6. `unavailable`: Tool or provider unavailable (Weight: 0.0).

---

## 3. Deterministic Confidence Engine

The Confidence Engine (`app.core.confidence.engine`) computes a 0–100 percentile score:
- **Priority:** `api / database > website > search > llm > assumption > unavailable`
- **Corroboration Boost:** +5 to +10 points when multiple distinct independent tools confirm findings.
- **Unavailable Tool Penalty:** -10 points per failed non-critical tool.
- **Data Freshness:** Timestamps >30 days apply a 10% freshness penalty.

---

## 4. Execution Lifecycle & Statuses

- **`COMPLETED`**: LLM and all requested tools executed successfully.
- **`DEGRADED`**: Partial tool failure or fallback LLM provider used, but actionable outputs were generated without data fabrication.
- **`UNAVAILABLE`**: Required APIs or network endpoints unreachable; fallback response returned with 0.0 confidence.
- **`FAILED`**: Exception encountered during execution; `agent.failed` event emitted to Redis event bus.

---

## 5. LLM Router & Fallback Chain

| Agent | Primary LLM Provider | Fallback Sequence |
|---|---|---|
| **Business Analysis Agent** | Gemini (`gemini-2.5-flash`) | Claude $\rightarrow$ OpenAI $\rightarrow$ DeepSeek $\rightarrow$ Qwen $\rightarrow$ OpenRouter |
| **SEO Audit Agent** | DeepSeek | OpenAI $\rightarrow$ Gemini $\rightarrow$ Claude |
| **Competitor Research Agent** | Gemini | OpenAI $\rightarrow$ Claude |
| **Marketing Strategy Agent** | Claude | Gemini $\rightarrow$ OpenAI |
| **Campaign Planner Agent** | OpenAI (`gpt-4o`) | Claude $\rightarrow$ Gemini |

---

## 6. Real-Time SSE Events (`RealtimeEvent`)

- `agent.started`
- `agent.tool.started`
- `agent.tool.completed`
- `agent.evidence.collected`
- `agent.llm.started`
- `agent.llm.completed`
- `agent.validation.completed`
- `agent.completed`
- `agent.failed`
