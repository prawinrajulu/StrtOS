# StrtOS AI Intelligence & Real Tool Execution Architecture

This document details the production LLM routing, fallback system, real tool registry, and execution monitoring layer for StrtOS.

---

## 1. LLM Provider Architecture & Routing Matrix

| Agent | Primary LLM Provider | Fallback Sequence |
|---|---|---|
| **Business Analysis Agent** | Gemini (`gemini-1.5-flash`) | Claude $\rightarrow$ OpenAI $\rightarrow$ DeepSeek $\rightarrow$ Qwen $\rightarrow$ OpenRouter |
| **SEO Audit Agent** | DeepSeek | OpenAI $\rightarrow$ Gemini $\rightarrow$ Claude |
| **Competitor Research Agent** | Gemini | OpenAI $\rightarrow$ Claude |
| **Marketing Strategy Agent** | Claude | Gemini $\rightarrow$ OpenAI |
| **Campaign Planner Agent** | OpenAI (`gpt-4o`) | Claude $\rightarrow$ Gemini |

### Standard Response Format (`LLMResponse`)
```json
{
  "content": "{...}",
  "provider": "Claude",
  "model": "claude-3-5-sonnet",
  "status": "SUCCESS",
  "error_code": null,
  "error_message": null,
  "retryable": false,
  "prompt_tokens": 420,
  "completion_tokens": 350,
  "total_tokens": 770,
  "estimated_cost_usd": 0.0012,
  "latency_seconds": 0.41
}
```

---

## 2. Real Tool Registry

- **Firecrawl**: Real web scraping and DOM markdown extraction (`https://api.firecrawl.dev/v1/scrape`).
- **Tavily**: Real-time web search and market research discovery.
- **Serper.dev**: Real Google SERP competitor index inspection.
- **Google PageSpeed Insights**: Core Web Vitals audit (`https://www.googleapis.com/pagespeedonline/v5/runPagespeed`).
- **Google Business / Places**: Google Maps business rating & review metrics.
- **Browser**: HTTP rendering and headers verification.

---

## 3. Fallback & Fail-Safe Strategy
When external API keys are missing or an API returns an error status:
1. The tool/provider returns a structured `UNAVAILABLE` payload (`error_code: NOT_CONFIGURED` or `HTTP_XXX`).
2. Fake simulated data is **NEVER** fabricated.
3. Downstream agent handlers inspect tool availability and execute safely with explicit warning flags.
