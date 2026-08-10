# StrtOS Adaptive Agent Learning & Self-Optimization

The Learning module implements StrtOS v1.5.0 Adaptive Learning, performance telemetry tracking, tool & LLM provider reliability scoring, bounded adaptation policies, policy versioning, automatic degradation rollback, and Governance escalation.

## Core Rules & Architecture
- **Deterministic Reliability Score**: Weighted formula across Prediction Accuracy (30%), Outcome Success (25%), Evidence Quality (15%), Human Approval (10%), Tool Reliability (10%), Swarm Consensus (5%), and Execution Stability (5%).
- **Bounded Adaptation**: Enforces `MAX_ADAPTATION_DELTA = 10.0%`, requiring verified outcomes. High deltas (> 5%) route through Governance `ApprovalRequest`.
- **Policy Versioning & Rollback**: `AgentPolicyModel` tracks versioned configurations (`DRAFT`, `TESTING`, `ACTIVE`, `ROLLED_BACK`, `DEPRECATED`). `PolicyRollbackEngine` automatically triggers rollback on performance drops (> 15%).
- **Multi-Tenant Security**: Enforces `organization_id == current_user.organization_id`.
