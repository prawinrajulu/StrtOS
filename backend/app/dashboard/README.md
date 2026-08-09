# StrtOS Executive Dashboard Module Architecture

The `backend/app/dashboard/` module aggregates multi-tenant analytical metrics from Supabase PostgreSQL.

## Architecture

- `schemas.py`: Pydantic V2 response DTOs (`DashboardOverviewResponse`, `ClientKPIs`, `WorkflowKPIs`, `TaskKPIs`, `ReportKPIs`, `AgentPerformanceItem`, `IndustryAnalyticsItem`, `TrendPoint`).
- `repository.py`: Tenant-isolated SQL aggregation queries (`COUNT`, `AVG`, `GROUP BY`) filtering strictly by `organization_id`.
- `service.py`: Service layer assembling overview metrics and generating deterministic executive insights.
- `routes.py`: REST API endpoints for `/api/v1/dashboard/*`.
