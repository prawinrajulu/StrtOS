# StrtOS - Database Migration Guide

Version: 1.0.0

Status: Development Ready

Owner: Database Engineering Team

Priority: Critical

---

# Purpose

This document defines the database migration strategy for StrtOS.

All schema changes must be managed through Alembic migrations.

Direct modification of the production database is strictly prohibited.

---

# Technology

PostgreSQL

SQLAlchemy 2.0

Alembic

UUID Primary Keys

JSONB

TIMESTAMP WITH TIME ZONE

---

# Migration Principles

Every schema change must

Be reversible

Be version controlled

Be reviewed

Be tested

Support rollback

---

# Migration Folder

backend/

alembic/

versions/

↓

0001_initial_schema.py

0002_users.py

0003_clients.py

0004_workflows.py

0005_tasks.py

0006_reports.py

0007_events.py

0008_memory.py

0009_tools.py

0010_notifications.py

---

# Initial Migration

Create

organizations

users

clients

workflows

tasks

reports

events

agent_memory

tool_registry

notifications

audit_logs

---

# organizations

Columns

id UUID

name

industry

email

subscription

status

created_at

updated_at

---

# users

Columns

id UUID

organization_id

name

email

password_hash

role

status

last_login

created_at

updated_at

---

# clients

Columns

id UUID

organization_id

business_name

industry

website

budget

goal

status

created_at

updated_at

---

# workflows

Columns

id UUID

client_id

workflow_type

workflow_status

overall_confidence

started_at

completed_at

created_at

---

# tasks

Columns

id UUID

workflow_id

agent_name

priority

status

retry_count

confidence

execution_time

created_at

completed_at

---

# reports

Columns

id UUID

workflow_id

business_summary

seo_summary

marketing_summary

analytics_summary

recommendations

overall_confidence

generated_at

---

# workflow_events

Columns

id UUID

workflow_id

event_name

event_type

agent_name

status

metadata JSONB

created_at

---

# agent_memory

Columns

id UUID

agent_name

memory_type

reference_id

content JSONB

importance

created_at

---

# tool_registry

Columns

id UUID

tool_name

provider

status

version

authentication_type

last_used

---

# notifications

Columns

id UUID

user_id

title

message

type

status

created_at

---

# audit_logs

Columns

id UUID

user_id

action

resource

ip_address

device

created_at

---

# Relationships

Organization

↓

Users

Organization

↓

Clients

Client

↓

Workflow

Workflow

↓

Tasks

Workflow

↓

Reports

Workflow

↓

Events

---

# Indexes

Create indexes on

organization_id

client_id

workflow_id

agent_name

status

created_at

---

# Constraints

Email Unique

Workflow UUID Unique

Client UUID Unique

Foreign Keys Required

Cascade Rules

ON DELETE RESTRICT

ON UPDATE CASCADE

---

# JSONB Usage

Store

Workflow Context

Memory

Metadata

Recommendations

Tool Outputs

Agent Config

---

# Rollback Strategy

Every migration must include

upgrade()

↓

downgrade()

No migration without rollback.

---

# Migration Naming

0001_initial_schema

0002_add_users

0003_add_clients

0004_add_workflows

...

Always incremental.

---

# Development Workflow

Developer creates migration

↓

Code Review

↓

Testing

↓

Staging

↓

Production

---

# Backup Policy

Backup before migration

Verify backup

Run migration

Verify integrity

Enable rollback if needed

---

# Future Tables

campaigns

seo_reports

marketing_strategies

knowledge_base

vector_embeddings

documents

crm

billing

organizations_settings

model_usage_logs

---

# Success Criteria

Database migrations are successful when

Every migration is reversible

No data loss occurs

Schema remains consistent

Foreign keys remain valid

Indexes improve performance

Production deployment is safe