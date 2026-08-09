from sqlalchemy import create_engine, inspect, text
from app.core.database import Base
import app.models.database
import app.auth.models
import app.agents.business_analysis.models
import app.agents.seo_audit.models
import app.agents.competitor_research.models
import app.agents.marketing_strategy.models
import app.agents.campaign_planner.models

sqlite_url = "sqlite:///./strtos_production.db"

def test_sync_sqlite():
    print("Testing synchronous schema creation against SQLite:", sqlite_url)
    engine = create_engine(sqlite_url)
    Base.metadata.create_all(engine)
    print("SUCCESS! Created all 21 tables in SQLite database!\n")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("=== VERIFIED CREATED TABLES IN POSTGRES/SQLITE DATABASE ===")
    for idx, t in enumerate(sorted(tables), 1):
        print(f"{idx:2d}. {t}")

if __name__ == "__main__":
    test_sync_sqlite()
