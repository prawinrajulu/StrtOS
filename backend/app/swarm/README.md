# StrtOS Multi-Agent Collaboration, Debate & Swarm Orchestration

The Swarm module implements StrtOS v1.4.0 Multi-Agent Swarm Intelligence. It orchestrates parallel execution of StrtOS 5 Core Specialist Agents, thread-safe shared context distribution, bounded agent debate rounds, critic quality scoring, conflict resolution, consensus calculation, governance escalation, and proposal routing to v1.3 Action Execution Engine.

## Core Rules & Architecture
- **5 Core Specialist Agents**: Business Analysis, SEO Audit, Competitor Research, Marketing Strategy, Campaign Planner.
- **No Dynamic Spawning**: Only registered specialist agents are executed.
- **Bounded Debate**: Maximum 3 debate/challenge rounds per agent pair.
- **Governance Escalation**: Low consensus (< 60%) or critical conflicts automatically trigger Governance ApprovalRequests.
- **Evidence-Backed**: LLM output is non-authoritative; all decisions are grounded in verified evidence items.
