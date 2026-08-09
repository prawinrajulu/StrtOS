import asyncio
from sqlalchemy import text
from app.core.database import engine

columns_to_add_reports = [
    ("executive_summary", "TEXT"),
    ("report_type", "VARCHAR DEFAULT 'EXECUTIVE_SUMMARY'"),
    ("status", "VARCHAR DEFAULT 'FINAL'"),
    ("overall_score", "INTEGER DEFAULT 92"),
    ("confidence_score", "FLOAT DEFAULT 95.0"),
    ("key_findings", "JSON"),
    ("recommendations", "JSON"),
    ("agent_results", "JSON"),
    ("metrics", "JSON"),
    ("created_by", "VARCHAR"),
    ("updated_at", "TIMESTAMP WITH TIME ZONE"),
]

async def migrate_reports_table():
    print("Migrating Supabase PostgreSQL 'reports' table...")
    async with engine.begin() as conn:
        for col_name, col_type in columns_to_add_reports:
            await conn.execute(text(f"ALTER TABLE reports ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            print(f" reports -> '{col_name}' verified.")

        # Ensure index on status and created_at
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_reports_status ON reports (status);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_reports_created_at ON reports (created_at);"))

    print("Reports Database Schema Sync Complete!")

if __name__ == "__main__":
    asyncio.run(migrate_reports_table())
