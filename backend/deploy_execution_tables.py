import asyncio
import sys
import os
from sqlalchemy import text
from app.core.database import engine

DDL_STATEMENTS = [
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'autonomymode') THEN
            CREATE TYPE autonomymode AS ENUM ('MANUAL', 'ASSISTED', 'APPROVAL_REQUIRED', 'AUTONOMOUS');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'policydecision') THEN
            CREATE TYPE policydecision AS ENUM ('ALLOW', 'DENY', 'REQUIRE_APPROVAL', 'EXPIRED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'actionstatus') THEN
            CREATE TYPE actionstatus AS ENUM ('DRAFT', 'PENDING_POLICY', 'PENDING_APPROVAL', 'APPROVED', 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'ROLLED_BACK', 'EXPIRED', 'DEGRADED');
        END IF;
    END $$;
    """,
    """
    CREATE TABLE IF NOT EXISTS actions (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        client_id VARCHAR REFERENCES clients(id) ON DELETE CASCADE,
        workflow_id VARCHAR REFERENCES workflows(id) ON DELETE SET NULL,
        prediction_id VARCHAR REFERENCES predictions(id) ON DELETE SET NULL,
        approval_id VARCHAR REFERENCES approval_requests(id) ON DELETE SET NULL,
        created_by VARCHAR,
        action_type VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        description TEXT,
        status actionstatus NOT NULL DEFAULT 'DRAFT',
        risk_level risklevel NOT NULL DEFAULT 'LOW',
        autonomy_mode autonomymode NOT NULL DEFAULT 'APPROVAL_REQUIRED',
        policy_decision policydecision NOT NULL DEFAULT 'REQUIRE_APPROVAL',
        input_payload JSONB,
        validated_payload JSONB,
        output_payload JSONB,
        error_message TEXT,
        retry_count INT DEFAULT 0,
        max_retries INT DEFAULT 3,
        idempotency_key VARCHAR,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        extra_metadata JSONB
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_actions_organization_id ON actions(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_actions_client_id ON actions(client_id);",
    "CREATE INDEX IF NOT EXISTS ix_actions_workflow_id ON actions(workflow_id);",
    "CREATE INDEX IF NOT EXISTS ix_actions_prediction_id ON actions(prediction_id);",
    "CREATE INDEX IF NOT EXISTS ix_actions_approval_id ON actions(approval_id);",
    "CREATE INDEX IF NOT EXISTS ix_actions_status ON actions(status);",
    "CREATE INDEX IF NOT EXISTS ix_actions_action_type ON actions(action_type);",
    "CREATE INDEX IF NOT EXISTS ix_actions_idempotency_key ON actions(idempotency_key);",
    "CREATE INDEX IF NOT EXISTS ix_actions_created_at ON actions(created_at);"
]

async def deploy():
    print("Connecting to live Supabase PostgreSQL database to deploy 'actions' table...")
    async with engine.begin() as conn:
        for stmt in DDL_STATEMENTS:
            await conn.execute(text(stmt))
        print("  [DDL Execution] 'actions' DDL executed successfully.")

        # Verification Query
        res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'actions'"))
        columns = res.fetchall()
        print(f"  [Verification] Found {len(columns)} columns in 'actions' table:")
        for col in columns[:8]:
            print(f"    - {col[0]}: {col[1]}")

        idx_res = await conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'actions'"))
        indexes = idx_res.fetchall()
        print(f"  [Verification] Found {len(indexes)} indexes on 'actions' table:")
        for idx in indexes:
            print(f"    - {idx[0]}")

if __name__ == "__main__":
    asyncio.run(deploy())
