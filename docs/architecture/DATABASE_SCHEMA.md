# StrtOS - Database Schema

Version: 1.0.0

Status: Approved

Component: Database Architecture

---

# Purpose

This document defines the complete database architecture of StrtOS.

It specifies

- Core Tables
- Relationships
- Primary Keys
- Foreign Keys
- Agent Data
- Workflow Data
- Reports
- Memory
- Event Logs

The database is the single source of truth for the entire platform.

---

# Database Engine

PostgreSQL

Reason

- ACID Compliance
- High Performance
- JSON Support
- Scalability
- Enterprise Ready

---

# Database Overview

Organization

↓

Users

↓

Clients

↓

Projects

↓

Workflows

↓

Tasks

↓

Agents

↓

Reports

↓

Events

↓

Memory

↓

Notifications

---

# organizations

Stores organizations using StrtOS.

Columns

id (UUID)

name

industry

email

phone

subscription_plan

created_at

updated_at

---

# users

Stores all users.

Columns

id (UUID)

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

Stores client businesses.

Columns

id (UUID)

organization_id

business_name

industry

website

location

target_audience

budget

goal

status

created_at

updated_at

---

# workflows

Stores CEO workflows.

Columns

id (UUID)

client_id

workflow_type

workflow_status

started_at

completed_at

overall_confidence

created_at

updated_at

---

# tasks

Stores every task.

Columns

id (UUID)

workflow_id

assigned_agent

task_name

priority

status

dependency

retry_count

eta

confidence

started_at

completed_at

---

# agents

Stores agent information.

Columns

id (UUID)

agent_name

description

version

status

health

latency

last_execution

supported_tasks

created_at

---

# reports

Stores executive reports.

Columns

id (UUID)

workflow_id

business_summary

seo_summary

competitor_summary

marketing_summary

campaign_summary

analytics_summary

recommendations

overall_confidence

generated_at

---

# workflow_events

Stores workflow timeline.

Columns

id (UUID)

workflow_id

event_name

event_type

agent_name

status

timestamp

metadata (JSONB)

---

# agent_memory

Stores long-term memory.

Columns

id (UUID)

agent_name

memory_type

reference_id

content (JSONB)

importance

created_at

---

# tool_registry

Stores external tools.

Columns

id (UUID)

tool_name

provider

status

version

authentication_type

last_used

---

# notifications

Stores notifications.

Columns

id (UUID)

user_id

title

message

type

status

created_at

---

# audit_logs

Stores security logs.

Columns

id (UUID)

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

Agent

↓

Memory

---

# Indexes

Create indexes for

organization_id

client_id

workflow_id

agent_name

status

created_at

---

# JSON Columns

Use JSONB for

metadata

memory

recommendations

tool_output

workflow_context

---

# Soft Delete

Every important table includes

deleted_at

Instead of permanent deletion.

---

# Naming Convention

Primary Key

id

Foreign Keys

organization_id

client_id

workflow_id

user_id

Snake Case

Always

---

# Future Tables

campaigns

seo_reports

competitor_reports

marketing_strategies

knowledge_base

vector_embeddings

documents

uploaded_files

ai_models

prompt_library

---

# Database Rules

Never duplicate client information.

Never duplicate workflow data.

Every task belongs to one workflow.

Every report belongs to one workflow.

Every workflow belongs to one client.

Every client belongs to one organization.

Every event belongs to one workflow.

Every memory belongs to one agent.

---

# Scalability

Support

100 Organizations

10,000 Clients

100,000 Workflows

1 Million Tasks

Millions of Events

No schema redesign required.

---

# Backup Strategy

Daily Backup

Incremental Backup

Point-in-Time Recovery

Disaster Recovery Ready

---

# Security

UUID Primary Keys

Encrypted Passwords

Audit Logs

Role Based Access

Soft Deletes

Prepared Statements

SQL Injection Protection

---

# Success Criteria

The database should

Store all business data

Store workflows

Store tasks

Store reports

Store events

Store memory

Support enterprise scaling

Maintain referential integrity

Support future AI features

without redesign.