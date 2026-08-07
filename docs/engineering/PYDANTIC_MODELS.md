# StrtOS - Pydantic Models Specification

Version: 1.0.0

Status: Development Ready

Owner: Backend Engineering Team

Priority: Critical

---

# Purpose

This document defines all Pydantic models used throughout StrtOS.

Every API endpoint, AI Agent, Workflow and Event must use these models.

No raw dictionaries should be passed between modules.

---

# Technology

Python 3.12+

Pydantic v2

FastAPI

UUID

Datetime

Enums

---

# Folder Structure

backend/

app/

schemas/

auth.py

organization.py

user.py

client.py

workflow.py

task.py

agent.py

memory.py

report.py

dashboard.py

notification.py

common.py

---

# Base Schema

Every schema inherits

BaseSchema

Contains

id

created_at

updated_at

---

# Organization

OrganizationCreate

Fields

name

industry

email

phone

website

subscription

---

OrganizationResponse

id

name

industry

status

created_at

---

# User

UserCreate

name

email

password

role

organization_id

---

UserLogin

email

password

---

UserResponse

id

name

email

role

organization

---

# Authentication

LoginRequest

email

password

---

LoginResponse

access_token

refresh_token

expires_in

user

---

RefreshTokenRequest

refresh_token

---

# Client

ClientCreate

business_name

industry

website

budget

goal

location

description

---

ClientUpdate

All optional fields

---

ClientResponse

id

business_name

industry

website

status

created_at

---

# CEO Directive

DirectiveRequest

business_name

industry

website

goal

budget

target_audience

priority

urgency

extra_context

---

DirectiveResponse

workflow_id

status

workflow

estimated_duration

confidence

---

# Workflow

WorkflowCreate

workflow_type

client_id

priority

---

WorkflowResponse

id

status

progress

current_state

started_at

completed_at

---

# Task

TaskResponse

id

workflow_id

agent_name

priority

status

confidence

execution_time

---

# Agent

AgentResponse

id

name

category

status

health

model

tools

latency

---

# Memory

MemoryEntry

memory_type

reference_id

content

importance

created_at

---

# Reports

BusinessReport

summary

strengths

weaknesses

opportunities

recommendations

---

SEOReport

technical_score

keywords

issues

recommendations

---

MarketingReport

channels

budget

campaigns

expected_roi

---

AnalyticsReport

traffic

conversion

growth

roi

insights

---

ExecutiveReport

workflow_id

business

seo

marketing

analytics

recommendations

overall_confidence

---

# Dashboard

DashboardOverview

organizations

clients

running_workflows

active_agents

reports

notifications

---

DashboardMetrics

workflow_success_rate

agent_success_rate

average_execution_time

api_latency

---

# Notifications

NotificationResponse

id

title

message

type

status

created_at

---

# Event Schema

WorkflowEvent

event_id

workflow_id

agent_name

event_type

status

timestamp

payload

---

# Common Enums

WorkflowStatus

CREATED

PLANNING

RUNNING

VALIDATING

REPORTING

COMPLETED

FAILED

---

AgentStatus

IDLE

RUNNING

WAITING

FAILED

OFFLINE

---

Priority

LOW

MEDIUM

HIGH

CRITICAL

---

# Validation Rules

Email

Valid Email

Website

Valid URL

Budget

Positive Number

UUID

Required

Confidence

0-100

Priority

Enum Only

---

# Error Schema

ErrorResponse

success

error_code

message

details

timestamp

---

# API Standard

Every endpoint returns

{
    "success": true,
    "message": "",
    "data": {}
}

Errors

{
    "success": false,
    "error": {},
    "timestamp": ""
}

---

# Future Models

Billing

CRM

Invoices

Meetings

Documents

Knowledge Base

Vector Memory

Plugin Registry

Marketplace

---

# Success Criteria

All APIs use Pydantic models

Validation is automatic

Frontend contracts remain stable

Schemas are reusable

Strong typing is maintained

Supports enterprise scalability