# StrtOS v1.4.0 — Multi-Agent Collaboration, Debate & Swarm Orchestration Architecture

## Overview
StrtOS v1.4.0 introduces **Multi-Agent Collaboration, Debate & Swarm Orchestration**. This milestone upgrades StrtOS from a sequential agent pipeline into a collaborative multi-agent swarm system. The existing 5 specialist agents (Business Analysis, SEO Audit, Competitor Research, Marketing Strategy, Campaign Planner) execute in parallel via a `SwarmCoordinator`, communicate across a secure `SharedContextBus`, challenge findings via a bounded `DebateEngine`, evaluate logical consistency via a `CriticEngine`, resolve contradictions via a `ConflictEngine`, and compute deterministic consensus via a `ConsensusEngine`. Low-consensus or high-risk outcomes escalate to human Governance, while final proposals route through the v1.3 `ActionRegistry` and `ExecutionEngine`.

---

## Swarm Collaboration Architecture Diagram

```
                         CEO
                          │
                          ▼
                  SWARM COORDINATOR
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Business       SEO       Competitor
          Analysis       Audit      Research
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                  SHARED CONTEXT BUS
                          │
                          ▼
                     DEBATE ENGINE
                          │
                          ▼
                    CRITIC ENGINE
                          │
                          ▼
                  CONFLICT ENGINE
                          │
                          ▼
                  CONSENSUS ENGINE
                          │
                          ▼
                    CEO SYNTHESIS
                          │
                          ▼
                    GOVERNANCE
                          │
                          ▼
                    EXECUTION
                          │
                          ▼
                    OUTCOME
                          │
                          ▼
                     MEMORY
```

---

## Core Principles & Security Guarantee

1. **Non-Authoritative LLMs**:
   - LLMs are reasoning components, NOT trusted authorities.
   - Every agent recommendation is evidence-backed, tenant-scoped, traceable, and confidence-scored.
   - LLM outputs never bypass Evidence, Governance, Policy Engine, Action Registry, or Execution Engine.

2. **No Unbounded Spawning**:
   - Swarms execute only the predefined 5 core specialist agents. Dynamic creation of unlimited new agents is strictly forbidden.

3. **Bounded Debate Rounds**:
   - Agent-to-agent debate rounds are capped at a maximum of 3 rounds per pair to prevent infinite loops.

4. **Human Governance Escalation**:
   - If consensus score is < 60% OR any CRITICAL conflict is detected, the swarm automatically creates an `ApprovalRequest` in Governance.

---

## Key Components

1. **Database Schema**:
   - `swarm_sessions` (23 columns, 6 indexes)
   - `swarm_messages` (10 columns, 3 indexes)
   - `swarm_conflicts` (14 columns, 3 indexes)
   - `swarm_debates` (10 columns, 3 indexes)

2. **Swarm Coordinator (`coordinator.py`)**:
   - Parallel execution of independent agents via `asyncio.gather` (Stage 1: Business Analysis, SEO Audit, Competitor Research -> Stage 2: Marketing Strategy -> Stage 3: Campaign Planner).

3. **Shared Context Bus (`context_bus.py`)**:
   - Thread-safe, tenant-isolated distribution of messages and evidence items between specialist agents.

4. **Debate, Critic, Conflict & Consensus Engines**:
   - `DebateEngine`: Capped challenge/question rounds.
   - `CriticEngine`: Logical consistency & evidence coverage scoring.
   - `ConflictEngine`: Contradictions classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
   - `ConsensusEngine`: Deterministic consensus score calculation and governance escalation triggers.
