import asyncio
import sys
import os
from sqlalchemy import text
from app.core.database import engine

DDL_STATEMENTS = [
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'scenariotype') THEN
            CREATE TYPE scenariotype AS ENUM ('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', 'CUSTOM');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'predictionstatus') THEN
            CREATE TYPE predictionstatus AS ENUM ('DRAFT', 'GENERATED', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'EXECUTED', 'MEASURED', 'EXPIRED', 'DEGRADED', 'UNAVAILABLE');
        END IF;
    END $$;
    """,
    """
    CREATE TABLE IF NOT EXISTS predictions (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        client_id VARCHAR REFERENCES clients(id) ON DELETE CASCADE,
        workflow_id VARCHAR REFERENCES workflows(id) ON DELETE SET NULL,
        report_id VARCHAR REFERENCES reports(id) ON DELETE SET NULL,
        approval_id VARCHAR REFERENCES approval_requests(id) ON DELETE SET NULL,
        scenario_id VARCHAR,
        scenario_type scenariotype NOT NULL DEFAULT 'BALANCED',
        scenario_name VARCHAR NOT NULL,
        objective TEXT,
        metric_name VARCHAR NOT NULL DEFAULT 'ROAS',
        predicted_value FLOAT NOT NULL,
        lower_bound FLOAT,
        upper_bound FLOAT,
        unit VARCHAR DEFAULT 'x',
        currency VARCHAR DEFAULT 'USD',
        confidence_score FLOAT DEFAULT 85.0,
        risk_score FLOAT DEFAULT 45.0,
        risk_level risklevel NOT NULL DEFAULT 'MEDIUM',
        evidence_count INT DEFAULT 0,
        memory_count INT DEFAULT 0,
        provider VARCHAR,
        model VARCHAR,
        assumptions JSONB,
        evidence_references JSONB,
        memory_references JSONB,
        prediction_status predictionstatus NOT NULL DEFAULT 'GENERATED',
        created_by VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        valid_until TIMESTAMP WITH TIME ZONE,
        extra_metadata JSONB
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_predictions_organization_id ON predictions(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_predictions_client_id ON predictions(client_id);",
    "CREATE INDEX IF NOT EXISTS ix_predictions_workflow_id ON predictions(workflow_id);",
    "CREATE INDEX IF NOT EXISTS ix_predictions_scenario_type ON predictions(scenario_type);",
    "CREATE INDEX IF NOT EXISTS ix_predictions_prediction_status ON predictions(prediction_status);",
    "CREATE INDEX IF NOT EXISTS ix_predictions_created_at ON predictions(created_at);"
]

async def deploy():
    print("Connecting to live Supabase PostgreSQL database to deploy 'predictions' table...")
    async with engine.begin() as conn:
        for stmt in DDL_STATEMENTS:
            await conn.execute(text(stmt))
        print("  [DDL Execution] 'predictions' DDL executed successfully.")

        # Verification Query
        res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'predictions'"))
        columns = res.fetchall()
        print(f"  [Verification] Found {len(columns)} columns in 'predictions' table:")
        for col in columns[:8]:
            print(f"    - {col[0]}: {col[1]}")

        idx_res = await conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'predictions'"))
        indexes = idx_res.fetchall()
        print(f"  [Verification] Found {len(indexes)} indexes on 'predictions' table:")
        for idx in indexes:
            print(f"    - {idx[0]}")

if __name__ == "__main__":
    asyncio.run(deploy())
