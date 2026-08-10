# StrtOS Adaptive Intelligence & Memory Layer

The Memory module provides StrtOS v1.1.0 with persistent historical memory, deterministic relevance ranking, outcome variance evaluation, and learned lesson extraction.

## Features
- **Unified Memory Model**: Stores `CLIENT_CONTEXT`, `DECISION`, `STRATEGY`, `APPROVAL`, `WORKFLOW`, `OUTCOME`, `FEEDBACK`, and `LESSON` records.
- **Deterministic Retrieval Engine**: Scores candidate memories based on Client Match, Industry Match, Keyword Overlap, Recency, Importance/Confidence, and Outcome status.
- **Outcome Variance Evaluator**: Calculates variance between AI prediction vs actual metrics (`SUCCESS` <=10%, `PARTIAL` 10-30%, `FAILED` >30%).
- **Deterministic Lesson Generator**: Grounded lesson extraction without LLM hallucination.
