"""initial_production_schema

Revision ID: 6cf730da4d22
Revises: 
Create Date: 2026-08-08 08:21:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6cf730da4d22'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Base Core Models
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('tier', sa.String(), nullable=True, server_default='ENTERPRISE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=True, server_default='FOUNDER'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)

    op.create_table(
        'clients',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('health_score', sa.Integer(), nullable=True, server_default='90'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_organization_id'), 'clients', ['organization_id'], unique=False)

    op.create_table(
        'workflows',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True, server_default='RUNNING'),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='92.0'),
        sa.Column('total_stages', sa.Integer(), nullable=True, server_default='9'),
        sa.Column('completed_stages', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_client_id'), 'workflows', ['client_id'], unique=False)

    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True, server_default='HIGH'),
        sa.Column('status', sa.String(), nullable=True, server_default='WAITING'),
        sa.Column('eta', sa.String(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_workflow_id'), 'tasks', ['workflow_id'], unique=False)

    op.create_table(
        'reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_workflow_id'), 'reports', ['workflow_id'], unique=False)

    op.create_table(
        'workflow_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_events_workflow_id'), 'workflow_events', ['workflow_id'], unique=False)

    # 2. Enterprise Auth Models
    op.create_table(
        'auth_organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_auth_organizations_slug'), 'auth_organizations', ['slug'], unique=True)

    op.create_table(
        'auth_roles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'auth_permissions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'auth_role_permissions',
        sa.Column('role_id', sa.String(), nullable=False),
        sa.Column('permission_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['auth_permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['auth_roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    op.create_table(
        'auth_users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'ORG_ADMIN', 'MANAGER', 'EMPLOYEE', 'VIEWER', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING', name='userstatus'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['auth_organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_auth_users_email'), 'auth_users', ['email'], unique=True)
    op.create_index(op.f('ix_auth_users_organization_id'), 'auth_users', ['organization_id'], unique=False)

    op.create_table(
        'auth_refresh_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_auth_refresh_tokens_token'), 'auth_refresh_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_auth_refresh_tokens_user_id'), 'auth_refresh_tokens', ['user_id'], unique=False)

    op.create_table(
        'auth_user_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_user_sessions_user_id'), 'auth_user_sessions', ['user_id'], unique=False)

    op.create_table(
        'auth_password_reset_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_auth_password_reset_tokens_token_hash'), 'auth_password_reset_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_auth_password_reset_tokens_user_id'), 'auth_password_reset_tokens', ['user_id'], unique=False)

    op.create_table(
        'auth_audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['auth_organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_audit_logs_action'), 'auth_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_auth_audit_logs_organization_id'), 'auth_audit_logs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_auth_audit_logs_user_id'), 'auth_audit_logs', ['user_id'], unique=False)

    # 3. Specialist Agent Models
    op.create_table(
        'business_analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=True),
        sa.Column('business_name', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('business_summary', sa.String(), nullable=False),
        sa.Column('digital_maturity_score', sa.Integer(), nullable=True, server_default='85'),
        sa.Column('business_maturity_score', sa.Integer(), nullable=True, server_default='80'),
        sa.Column('swot_json', sa.JSON(), nullable=True),
        sa.Column('personas_json', sa.JSON(), nullable=True),
        sa.Column('growth_opportunities_json', sa.JSON(), nullable=True),
        sa.Column('recommendations_json', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='95.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_analyses_workflow_id'), 'business_analyses', ['workflow_id'], unique=False)

    op.create_table(
        'seo_audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=False),
        sa.Column('overall_seo_score', sa.Integer(), nullable=True, server_default='88'),
        sa.Column('technical_seo_score', sa.Integer(), nullable=True, server_default='90'),
        sa.Column('on_page_seo_score', sa.Integer(), nullable=True, server_default='85'),
        sa.Column('performance_score', sa.Integer(), nullable=True, server_default='92'),
        sa.Column('accessibility_score', sa.Integer(), nullable=True, server_default='94'),
        sa.Column('core_web_vitals_json', sa.JSON(), nullable=True),
        sa.Column('critical_issues_json', sa.JSON(), nullable=True),
        sa.Column('warnings_json', sa.JSON(), nullable=True),
        sa.Column('recommendations_json', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='95.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seo_audits_workflow_id'), 'seo_audits', ['workflow_id'], unique=False)

    op.create_table(
        'competitor_researches',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=True),
        sa.Column('business_name', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('market_position_summary', sa.String(), nullable=False),
        sa.Column('direct_competitors_json', sa.JSON(), nullable=True),
        sa.Column('indirect_competitors_json', sa.JSON(), nullable=True),
        sa.Column('market_gaps_json', sa.JSON(), nullable=True),
        sa.Column('recommendations_json', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='95.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competitor_researches_workflow_id'), 'competitor_researches', ['workflow_id'], unique=False)

    op.create_table(
        'marketing_strategies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=True),
        sa.Column('brand_positioning', sa.String(), nullable=False),
        sa.Column('unique_value_proposition', sa.String(), nullable=False),
        sa.Column('roi_projection', sa.String(), nullable=False),
        sa.Column('channel_recommendations_json', sa.JSON(), nullable=True),
        sa.Column('budget_allocation_json', sa.JSON(), nullable=True),
        sa.Column('growth_roadmap_json', sa.JSON(), nullable=True),
        sa.Column('recommendations_json', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='95.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_marketing_strategies_workflow_id'), 'marketing_strategies', ['workflow_id'], unique=False)

    op.create_table(
        'campaign_plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=True),
        sa.Column('campaign_timeline', sa.String(), nullable=False),
        sa.Column('expected_outcome', sa.String(), nullable=False),
        sa.Column('channel_allocation_json', sa.JSON(), nullable=True),
        sa.Column('creative_requirements_json', sa.JSON(), nullable=True),
        sa.Column('weekly_roadmap_json', sa.JSON(), nullable=True),
        sa.Column('launch_checklist_json', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='95.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_plans_workflow_id'), 'campaign_plans', ['workflow_id'], unique=False)


def downgrade() -> None:
    op.drop_table('campaign_plans')
    op.drop_table('marketing_strategies')
    op.drop_table('competitor_researches')
    op.drop_table('seo_audits')
    op.drop_table('business_analyses')

    op.drop_table('auth_audit_logs')
    op.drop_table('auth_password_reset_tokens')
    op.drop_table('auth_user_sessions')
    op.drop_table('auth_refresh_tokens')
    op.drop_table('auth_users')
    op.drop_table('auth_role_permissions')
    op.drop_table('auth_permissions')
    op.drop_table('auth_roles')
    op.drop_table('auth_organizations')

    op.drop_table('workflow_events')
    op.drop_table('reports')
    op.drop_table('tasks')
    op.drop_table('workflows')
    op.drop_table('clients')
    op.drop_table('users')
    op.drop_table('organizations')
