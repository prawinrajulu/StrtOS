import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.core.database import Base
import app.models.database
import app.auth.models
import app.governance.models
import app.memory.models

# Connect using statement_cache_size=0 for Supabase Pooler compatibility
engine = create_async_engine(settings.DATABASE_URL, connect_args={"statement_cache_size": 0})

async def deploy():
    print("\n=======================================================")
    print("DEPLOYING MEMORY TABLES TO SUPABASE POSTGRESQL")
    print("=======================================================")
    print(f"Total Registered SQLAlchemy Metadata Tables: {len(Base.metadata.tables)}")
    print("Tables:", list(Base.metadata.tables.keys()))

    async with engine.begin() as conn:
        print("\nExecuting CREATE TABLE DDL for memory_records...")
        await conn.run_sync(Base.metadata.create_all)

    print("\nSUCCESS! DDL execution completed!")

    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"))
        tables = [row[0] for row in res.fetchall()]
        print("\n=======================================================")
        print(f"VERIFIED LIVE SUPABASE POSTGRESQL TABLES ({len(tables)} total):")
        print("=======================================================")
        for idx, t in enumerate(tables, 1):
            print(f"{idx:2d}. {t}")

if __name__ == "__main__":
    asyncio.run(deploy())
