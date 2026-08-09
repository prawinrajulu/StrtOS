# StrtOS Real-Time AI Execution & SSE Architecture

This document details the real-time event streaming architecture powering StrtOS AI workflow execution.

---

## 1. Event Flow

```
CEO Directive / Workflow Start
      ↓
CEO Orchestrator Pipeline
      ↓
EventPublisher (app/core/events/publisher.py)
      ↓
Redis Pub/Sub Event Bus (strtos_events, strtos_events:{workflow_id}, strtos_events_org:{org_id})
      ↓
FastAPI SSE Endpoints (/api/v1/ceo/stream, /api/v1/workflows/{workflow_id}/stream)
      ↓
React Frontend SSE Client (EventStreamClient in src/services/eventStream.ts)
      ↓
Live UI Updates (WorkflowDetailsPage, CEOAgentPage, DashboardPage)
```

---

## 2. Canonical Event Schema (`RealtimeEvent`)

```json
{
  "event_id": "b9437ac8-8066-4b08-9528-2727fd118efe",
  "event_type": "task.completed",
  "workflow_id": "wf-123456",
  "task_id": "task-abc",
  "agent_name": "SEO Audit Agent",
  "organization_id": "org-7890",
  "timestamp": "2026-08-09T14:55:02.638361+00:00",
  "status": "COMPLETED",
  "progress": 100,
  "message": "SEO audit task completed",
  "metadata": {}
}
```

---

## 3. Supported Event Types

- **Workflow Lifecycle**: `workflow.created`, `workflow.started`, `workflow.running`, `workflow.completed`, `workflow.failed`
- **Task Lifecycle**: `task.started`, `task.progress`, `task.completed`, `task.failed`
- **Agent Telemetry**: `agent.started`, `agent.thinking`, `agent.progress`, `agent.completed`
- **Report & Dashboard**: `report.created`, `dashboard.updated`

---

## 4. Multi-Tenant Event Security
- SSE endpoints strictly enforce JWT authentication and filter channel subscriptions by `organization_id` and `workflow_id`.
- Users from Organization B cannot subscribe to or receive event streams belonging to Organization A.
