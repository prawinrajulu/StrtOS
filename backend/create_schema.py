import asyncio
from app.core.database import engine, Base
import app.models.database
import app.auth.models
import app.agents.business_analysis.models
import app.agents.seo_audit.models
import app.agents.competitor_research.models
import app.agents.marketing_strategy.models
import app.agents.campaign_planner.models

async def main():
    print("Tables registered in metadata:", list(Base.metadata.tables.keys()))
    print("Total Table Count:", len(Base.metadata.tables))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Schema Metadata Verification Complete!")

if __name__ == "__main__":
    asyncio.run(main())
