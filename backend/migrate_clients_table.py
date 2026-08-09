import asyncio
from sqlalchemy import text
from app.core.database import engine

columns_to_add = [
    ("website_url", "VARCHAR"),
    ("description", "TEXT"),
    ("business_goal", "TEXT"),
    ("monthly_budget", "DOUBLE PRECISION DEFAULT 0.0"),
    ("currency", "VARCHAR DEFAULT 'USD'"),
    ("status", "VARCHAR DEFAULT 'ACTIVE'"),
    ("contact_name", "VARCHAR"),
    ("contact_email", "VARCHAR"),
    ("contact_phone", "VARCHAR"),
    ("created_by", "VARCHAR"),
]

async def migrate_clients():
    print("Migrating Supabase PostgreSQL 'clients' table...")
    async with engine.begin() as conn:
        for col_name, col_type in columns_to_add:
            try:
                sql = f"ALTER TABLE clients ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                await conn.execute(text(sql))
                print(f" Column '{col_name}' verified/added.")
            except Exception as e:
                print(f" Error adding '{col_name}': {e}")
    print("Database Schema Sync Complete!")

if __name__ == "__main__":
    asyncio.run(migrate_clients())
