import asyncio
import sys
import os
from sqlalchemy import text
from app.core.database import engine

DDL_STATEMENTS = [
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'swarmstatus') THEN
            CREATE TYPE swarmstatus AS ENUM ('DRAFT', 'PLANNING', 'RUNNING', 'DEBATING', 'CRITIQUING', 'CONSENSUS', 'COMPLETED', 'DEGRADED', 'FAILED', 'CANCELLED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'swarmmessagetype') THEN
            CREATE TYPE swarmmessagetype AS ENUM ('FINDING', 'EVIDENCE', 'QUESTION', 'CRITIQUE', 'RECOMMENDATION', 'CONFLICT', 'CONSENSUS', 'DECISION');
        END IF;
    END $$;
    """,
    """
    CREATE TABLE IF NOT EXISTS swarm_sessions (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        client_id VARCHAR REFERENCES clients(id) ON DELETE CASCADE,
        workflow_id VARCHAR REFERENCES workflows(id) ON DELETE SET NULL,
        prediction_id VARCHAR REFERENCES predictions(id) ON DELETE SET NULL,
        status swarmstatus NOT NULL DEFAULT 'DRAFT',
        objective TEXT NOT NULL,
        strategy TEXT,
        participating_agents JSONB DEFAULT '[]'::jsonb,
        active_agents JSONB DEFAULT '[]'::jsonb,
        completed_agents JSONB DEFAULT '[]'::jsonb,
        failed_agents JSONB DEFAULT '[]'::jsonb,
        consensus_score FLOAT DEFAULT 0.0,
        confidence_score FLOAT DEFAULT 0.0,
        conflict_count INT DEFAULT 0,
        debate_rounds INT DEFAULT 0,
        synthesis_output JSONB,
        created_by VARCHAR,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        extra_metadata JSONB
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_swarm_sessions_organization_id ON swarm_sessions(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_sessions_client_id ON swarm_sessions(client_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_sessions_workflow_id ON swarm_sessions(workflow_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_sessions_prediction_id ON swarm_sessions(prediction_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_sessions_status ON swarm_sessions(status);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_sessions_created_at ON swarm_sessions(created_at);",
    """
    CREATE TABLE IF NOT EXISTS swarm_messages (
        id VARCHAR PRIMARY KEY,
        swarm_id VARCHAR NOT NULL REFERENCES swarm_sessions(id) ON DELETE CASCADE,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        source_agent VARCHAR NOT NULL,
        target_agent VARCHAR,
        message_type swarmmessagetype NOT NULL,
        content TEXT NOT NULL,
        evidence_refs JSONB DEFAULT '[]'::jsonb,
        confidence FLOAT DEFAULT 80.0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_swarm_messages_swarm_id ON swarm_messages(swarm_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_messages_organization_id ON swarm_messages(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_messages_created_at ON swarm_messages(created_at);",
    """
    CREATE TABLE IF NOT EXISTS swarm_conflicts (
        id VARCHAR PRIMARY KEY,
        swarm_id VARCHAR NOT NULL REFERENCES swarm_sessions(id) ON DELETE CASCADE,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        subject VARCHAR NOT NULL,
        agent_a VARCHAR NOT NULL,
        agent_b VARCHAR NOT NULL,
        claim_a TEXT NOT NULL,
        claim_b TEXT NOT NULL,
        evidence_a JSONB DEFAULT '[]'::jsonb,
        evidence_b JSONB DEFAULT '[]'::jsonb,
        severity risklevel NOT NULL DEFAULT 'MEDIUM',
        resolution TEXT,
        resolved_by VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_swarm_conflicts_swarm_id ON swarm_conflicts(swarm_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_conflicts_organization_id ON swarm_conflicts(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_conflicts_created_at ON swarm_conflicts(created_at);",
    """
    CREATE TABLE IF NOT EXISTS swarm_debates (
        id VARCHAR PRIMARY KEY,
        swarm_id VARCHAR NOT NULL REFERENCES swarm_sessions(id) ON DELETE CASCADE,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        round_number INT NOT NULL,
        claim TEXT NOT NULL,
        challenge TEXT NOT NULL,
        supporting_evidence JSONB DEFAULT '[]'::jsonb,
        counter_evidence JSONB DEFAULT '[]'::jsonb,
        resolution TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_swarm_debates_swarm_id ON swarm_debates(swarm_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_debates_organization_id ON swarm_debates(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_swarm_debates_created_at ON swarm_debates(created_at);"
]

async def deploy():
    print("Connecting to live Supabase PostgreSQL database to deploy Swarm tables...")
    async with engine.begin() as conn:
        for stmt in DDL_STATEMENTS:
            await conn.execute(text(stmt))
        print("  [DDL Execution] Swarm DDL executed successfully.")

        # Verification Queries
        tables = ['swarm_sessions', 'swarm_messages', 'swarm_conflicts', 'swarm_debates']
        for tbl in tables:
            res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tbl}'"))
            cols = res.fetchall()
            print(f"  [Verification] '{tbl}' table deployed with {len(cols)} columns.")

if __name__ == "__main__":
    asyncio.run(deploy())
