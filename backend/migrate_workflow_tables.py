import asyncio
from sqlalchemy import text
from app.core.database import engine

columns_to_add_workflows = [
    ("organization_id", "VARCHAR"),
    ("created_by", "VARCHAR"),
    ("directive", "TEXT"),
    ("active_stage", "VARCHAR DEFAULT 'INITIALIZATION'"),
    ("progress", "INTEGER DEFAULT 0"),
    ("started_at", "TIMESTAMP WITH TIME ZONE"),
    ("completed_at", "TIMESTAMP WITH TIME ZONE"),
]

columns_to_add_tasks = [
    ("organization_id", "VARCHAR"),
    ("description", "TEXT"),
    ("dependencies", "JSON"),
    ("max_retries", "INTEGER DEFAULT 3"),
    ("started_at", "TIMESTAMP WITH TIME ZONE"),
    ("completed_at", "TIMESTAMP WITH TIME ZONE"),
    ("error_message", "TEXT"),
    ("output", "JSON"),
]

columns_to_add_reports = [
    ("organization_id", "VARCHAR"),
    ("client_id", "VARCHAR"),
]

columns_to_add_events = [
    ("organization_id", "VARCHAR"),
]

async def migrate_workflow_tables():
    print("Migrating Supabase PostgreSQL 'workflows', 'tasks', 'reports', 'workflow_events' tables...")
    async with engine.begin() as conn:
        for col_name, col_type in columns_to_add_workflows:
            await conn.execute(text(f"ALTER TABLE workflows ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            print(f" workflows -> '{col_name}' verified.")

        for col_name, col_type in columns_to_add_tasks:
            await conn.execute(text(f"ALTER TABLE tasks ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            print(f" tasks -> '{col_name}' verified.")

        for col_name, col_type in columns_to_add_reports:
            await conn.execute(text(f"ALTER TABLE reports ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            print(f" reports -> '{col_name}' verified.")

        for col_name, col_type in columns_to_add_events:
            await conn.execute(text(f"ALTER TABLE workflow_events ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            print(f" workflow_events -> '{col_name}' verified.")

    print("Workflow Database Schema Sync Complete!")

if __name__ == "__main__":
    asyncio.run(migrate_workflow_tables())
