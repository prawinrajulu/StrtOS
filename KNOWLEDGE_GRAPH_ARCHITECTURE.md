# CAUSAL INTELLIGENCE & KNOWLEDGE GRAPH ARCHITECTURE (StrtOS v1.8.0)

## Overview

StrtOS v1.8.0 introduces the **Causal Intelligence & Knowledge Graph** layer. This system establishes structured, tenant-isolated directed relationships tracking causality across Evidence, Memory, Specialist Agents, Decisions, Predictions, Actions, Policies, Outcomes, Performance, and Lessons.

---

## Final StrtOS Intelligence Loop

```
REAL DATA
   ↓
EVIDENCE
   ↓
MEMORY
   ↓
KNOWLEDGE GRAPH
   ↓
CAUSAL INTELLIGENCE
   ↓
PREDICTION
   ↓
MULTI-AGENT SWARM
   ↓
GOVERNANCE
   ↓
EXECUTION
   ↓
ACTUAL OUTCOME
   ↓
ROOT-CAUSE ANALYSIS
   ↓
AGENT PERFORMANCE
   ↓
AGENT LEARNING
   ↓
POLICY EVOLUTION
   ↓
A/B VALIDATION
   ↓
VERSIONED POLICY
   ↓
BETTER FUTURE DECISION
   ↺
```

---

## Core Knowledge Entities

- **KnowledgeNode**: Represents system entities (`CLIENT`, `INDUSTRY`, `EVIDENCE`, `MEMORY`, `AGENT`, `DECISION`, `PREDICTION`, `ACTION`, `POLICY_VERSION`, `OUTCOME`, `LESSON`, `APPROVAL`, `WORKFLOW`).
- **KnowledgeRelation**: Directed causal link (`SUPPORTS`, `CONTRADICTS`, `INFLUENCED`, `CAUSED`, `CONTRIBUTED_TO`, `LED_TO`, `PRODUCED`, `VALIDATES`, `GOVERNED`, `INFLUENCES`).
- **CausalObservation**: Empirical observation tracking supporting vs contradicting evidence and deterministic causal confidence.

---

## Deterministic Causal Statuses

- `OBSERVED`: Observed co-occurrence without confirmed causality.
- `HYPOTHESIS`: Grounded hypothesis under evaluation.
- `SUPPORTED`: Empirically supported relationship.
- `VALIDATED`: Validated by independent consistent observations.
- `CONTRADICTED`: Contradicted by empirical observations.
- `INSUFFICIENT_DATA`: Insufficient data available (never fabricated).
