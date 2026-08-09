# StrtOS Client Management Module

## Architecture Overview
The Client Management Module provides strict multi-tenant Client isolation. Every Client belongs to exactly one Organization (`organization_id`).

## Key Endpoints
- `POST /api/v1/clients`: Create a Client (Scoped to authenticated user's `organization_id`)
- `GET /api/v1/clients`: List Clients for user's organization (with search, pagination, and status filters)
- `GET /api/v1/clients/{client_id}`: Retrieve a single Client (Verifies tenant ownership)
- `PATCH /api/v1/clients/{client_id}`: Update Client fields
- `DELETE /api/v1/clients/{client_id}`: Soft-delete / archive Client record
