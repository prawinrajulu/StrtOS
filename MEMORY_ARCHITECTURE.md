# StrtOS v1.1.0 — Adaptive Intelligence & Memory Layer Architecture

## Overview
StrtOS v1.1.0 introduces the **Adaptive Intelligence & Memory Layer**. This system records, indexes, scores, and retrieves historical client context, executive decisions, strategy recommendations, human approvals/rejections, workflow executions, and measured KPI outcomes to inform and refine future AI decisions without hallucinating historical facts.

---

## Memory Architecture Diagram

```
                        +-----------------------------------+
                        |    StrtOS REST API & Event Bus    |
                        |   - /api/v1/memory                |
                        |   - /api/v1/memory/outcomes       |
                        +-----------------+-----------------+
                                          |
                                          v
                        +-----------------------------------+
                        |   Memory Service & Multi-Tenant   |
                        |   Isolation (organization_id)     |
                        +--------+-----------------+--------+
                                 |                 |
            +--------------------+                 +--------------------+
            |                                                           |
            v                                                           v
+-----------------------------------+                       +-----------------------------------+
|  Deterministic Retrieval Engine   |                       |    Deterministic Outcome Engine   |
|  - Client Match (+40 pts)         |                       |  - Variance Evaluation (0-100%)   |
|  - Industry Match (+20 pts)       |                       |  - Status: SUCCESS, PARTIAL,      |
|  - Keyword Overlap (+15 pts)      |                       |           FAILED                  |
|  - Recency & Score (+25 pts)      |                       |  - Grounded Lesson Extractor      |
+-----------------+-----------------+                       +-----------------+-----------------+
                  |                                                           |
                  v                                                           v
+-----------------------------------------------------------------------------------------------+
|                                Live Supabase PostgreSQL DB                                    |
|                                - memory_records table                                         |
+-----------------------------------------------------------------------------------------------+
```

---

## Key Components

1. **Unified Database Model (`MemoryRecordModel`)**:
   - Single unified table (`memory_records`) supporting 8 memory types (`CLIENT_CONTEXT`, `DECISION`, `STRATEGY`, `APPROVAL`, `WORKFLOW`, `OUTCOME`, `FEEDBACK`, `LESSON`).
   - Tenant-scoped with mandatory Foreign Key `organization_id`.
   - Indexed on `organization_id`, `client_id`, `workflow_id`, `memory_type`, `created_at`, and `importance_score`.

2. **Deterministic Memory Retrieval Engine (`retrieval.py`)**:
   - Calculates a 0.0–100.0 relevance score per candidate record based on:
     - Exact Client Match (+40)
     - Industry Match (+20)
     - Keyword Overlap in Title/Content (+15)
     - Recency Factor (+10 for <= 30 days)
     - Importance & Confidence Weight (+15)
     - Historical Outcome Status (+5 for SUCCESS)

3. **Deterministic Outcome & Lesson Engine (`outcome_engine.py`)**:
   - Compares AI PREDICTED KPI vs ACTUAL KPI values:
     - Variance <= 10%: `SUCCESS`
     - Variance 10%–30%: `PARTIAL`
     - Variance > 30%: `FAILED`
   - Automatically extracts non-fabricated, evidence-grounded `LESSON` records.

4. **CEO Orchestrator & Specialist Agent Context Injection**:
   - Pre-retrieves top relevant historical signals before graph execution.
   - Strictly demarcates prompts into:
     - `CURRENT VERIFIED EVIDENCE`
     - `HISTORICAL MEMORY (DO NOT CITE AS CURRENT EXTERNAL SOURCE)`
     - `CURRENT BUSINESS CONTEXT`
     - `AI ASSUMPTIONS`

5. **Real-Time Event Broadcasting**:
   - Publishes `memory.created`, `memory.updated`, `outcome.recorded`, and `lesson.created` events via Redis Pub/Sub & SSE.
