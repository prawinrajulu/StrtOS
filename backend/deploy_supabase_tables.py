import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
import app.models.database
import app.auth.models
import app.agents.business_analysis.models
import app.agents.seo_audit.models
import app.agents.competitor_research.models
import app.agents.marketing_strategy.models
import app.agents.campaign_planner.models
from sqlalchemy import text

# Disable statement cache for Supabase Transaction Pooler (port 6543)
engine = create_async_engine(settings.DATABASE_URL, connect_args={"statement_cache_size": 0})

async def deploy():
    print("Connecting to live Supabase PostgreSQL database via Pooler (statement_cache_size=0)...")
    print("Registered tables in SQLAlchemy metadata:", len(Base.metadata.tables))
    
    async with engine.begin() as conn:
        print("Executing CREATE TABLE DDL statements on Supabase...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("\nSUCCESS! All tables created on Supabase!")
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"))
        tables = [row[0] for row in result.fetchall()]
        print("\n=======================================================")
        print(f"VERIFIED LIVE TABLES IN SUPABASE POSTGRESQL (Total: {len(tables)}):")
        print("=======================================================")
        for idx, t in enumerate(tables, 1):
            print(f"{idx:2d}. {t}")

if __name__ == "__main__":
    asyncio.run(deploy())
