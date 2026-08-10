import asyncio
import sys
import os
from sqlalchemy import text
from app.core.database import engine

DDL_STATEMENTS = [
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reliabilityclass') THEN
            CREATE TYPE reliabilityclass AS ENUM ('EXCELLENT', 'GOOD', 'MODERATE', 'LOW', 'CRITICAL', 'INSUFFICIENT_DATA');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'policystatus') THEN
            CREATE TYPE policystatus AS ENUM ('DRAFT', 'TESTING', 'ACTIVE', 'ROLLED_BACK', 'DEPRECATED');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'adaptationstatus') THEN
            CREATE TYPE adaptationstatus AS ENUM ('PROPOSED', 'PENDING_GOVERNANCE', 'APPROVED', 'ACTIVATED', 'REJECTED', 'ROLLED_BACK');
        END IF;
    END $$;
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_performance (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        client_id VARCHAR REFERENCES clients(id) ON DELETE CASCADE,
        agent_name VARCHAR NOT NULL,
        agent_version VARCHAR NOT NULL DEFAULT '1.0.0',
        total_executions INT DEFAULT 0,
        successful_executions INT DEFAULT 0,
        degraded_executions INT DEFAULT 0,
        failed_executions INT DEFAULT 0,
        average_confidence FLOAT DEFAULT 80.0,
        average_latency_ms FLOAT DEFAULT 0.0,
        average_token_usage INT DEFAULT 0,
        prediction_accuracy FLOAT DEFAULT 80.0,
        outcome_success_rate FLOAT DEFAULT 80.0,
        human_approval_rate FLOAT DEFAULT 90.0,
        human_rejection_rate FLOAT DEFAULT 10.0,
        swarm_consensus_rate FLOAT DEFAULT 85.0,
        tool_success_rate FLOAT DEFAULT 95.0,
        evidence_quality_score FLOAT DEFAULT 85.0,
        current_reliability_score FLOAT DEFAULT 80.0,
        reliability_class reliabilityclass NOT NULL DEFAULT 'INSUFFICIENT_DATA',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_agent_performance_organization_id ON agent_performance(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_agent_performance_agent_name ON agent_performance(agent_name);",
    """
    CREATE TABLE IF NOT EXISTS tool_reliability (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        tool_name VARCHAR NOT NULL,
        success_count INT DEFAULT 0,
        failure_count INT DEFAULT 0,
        timeout_count INT DEFAULT 0,
        average_latency_ms FLOAT DEFAULT 0.0,
        availability_rate FLOAT DEFAULT 100.0,
        evidence_quality FLOAT DEFAULT 85.0,
        reliability_score FLOAT DEFAULT 90.0,
        last_successful_execution TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_tool_reliability_organization_id ON tool_reliability(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_tool_reliability_tool_name ON tool_reliability(tool_name);",
    """
    CREATE TABLE IF NOT EXISTS llm_provider_performance (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        provider VARCHAR NOT NULL,
        model VARCHAR NOT NULL,
        agent_name VARCHAR,
        average_latency_ms FLOAT DEFAULT 0.0,
        average_token_usage INT DEFAULT 0,
        estimated_cost FLOAT DEFAULT 0.0,
        success_count INT DEFAULT 0,
        failure_count INT DEFAULT 0,
        retry_count INT DEFAULT 0,
        fallback_count INT DEFAULT 0,
        structured_output_success_rate FLOAT DEFAULT 95.0,
        confidence_score FLOAT DEFAULT 90.0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_llm_provider_performance_organization_id ON llm_provider_performance(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_llm_provider_performance_provider ON llm_provider_performance(provider);",
    """
    CREATE TABLE IF NOT EXISTS agent_policies (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        agent_name VARCHAR NOT NULL,
        policy_version VARCHAR NOT NULL,
        configuration JSONB NOT NULL,
        reason TEXT NOT NULL,
        evidence_count INT DEFAULT 0,
        confidence FLOAT DEFAULT 80.0,
        status policystatus NOT NULL DEFAULT 'ACTIVE',
        created_by VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_agent_policies_organization_id ON agent_policies(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_agent_policies_agent_name ON agent_policies(agent_name);",
    "CREATE INDEX IF NOT EXISTS ix_agent_policies_status ON agent_policies(status);",
    """
    CREATE TABLE IF NOT EXISTS agent_adaptations (
        id VARCHAR PRIMARY KEY,
        organization_id VARCHAR NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        agent_name VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        description TEXT NOT NULL,
        previous_performance JSONB,
        expected_improvement JSONB,
        adaptation_delta FLOAT DEFAULT 5.0,
        status adaptationstatus NOT NULL DEFAULT 'PROPOSED',
        approval_id VARCHAR REFERENCES approval_requests(id) ON DELETE SET NULL,
        policy_id VARCHAR REFERENCES agent_policies(id) ON DELETE SET NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_agent_adaptations_organization_id ON agent_adaptations(organization_id);",
    "CREATE INDEX IF NOT EXISTS ix_agent_adaptations_agent_name ON agent_adaptations(agent_name);",
    "CREATE INDEX IF NOT EXISTS ix_agent_adaptations_status ON agent_adaptations(status);"
]

async def deploy():
    print("Connecting to live Supabase PostgreSQL database to deploy Learning tables...")
    async with engine.begin() as conn:
        for stmt in DDL_STATEMENTS:
            await conn.execute(text(stmt))
        print("  [DDL Execution] Learning DDL executed successfully.")

        # Verification Queries
        tables = ['agent_performance', 'tool_reliability', 'llm_provider_performance', 'agent_policies', 'agent_adaptations']
        for tbl in tables:
            res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tbl}'"))
            cols = res.fetchall()
            print(f"  [Verification] '{tbl}' table deployed with {len(cols)} columns.")

if __name__ == "__main__":
    asyncio.run(deploy())
