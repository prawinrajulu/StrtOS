# StrtOS - API Specification

Version: 1.0.0

Status: Approved

Component: REST API Layer

---

# Purpose

This document defines every REST API used by StrtOS.

It includes

- Authentication APIs
- Client APIs
- Workflow APIs
- CEO Agent APIs
- Agent APIs
- Reports APIs
- Dashboard APIs
- Settings APIs

The API Layer is the only communication bridge between Frontend and Backend.

---

# API Architecture

React Frontend

↓

REST API

↓

FastAPI Backend

↓

CEO Agent

↓

Specialist Agents

↓

Database

---

# API Standards

Protocol

HTTPS

Format

JSON

Authentication

JWT Bearer Token

Encoding

UTF-8

Version

/api/v1/

---

# Response Format

Success

{
    "success": true,
    "message": "",
    "data": {}
}

Error

{
    "success": false,
    "error": "",
    "code": ""
}

---

# Authentication APIs

## Login

POST

/api/v1/auth/login

Purpose

Authenticate user.

Request

Email

Password

Response

JWT Token

User Details

Permissions

---

## Register

POST

/api/v1/auth/register

Purpose

Create organization and administrator.

---

## Logout

POST

/api/v1/auth/logout

---

## Refresh Token

POST

/api/v1/auth/refresh

---

## Current User

GET

/api/v1/auth/me

---

# Client APIs

## Get Clients

GET

/api/v1/clients

---

## Create Client

POST

/api/v1/clients

---

## Update Client

PUT

/api/v1/clients/{id}

---

## Delete Client

DELETE

/api/v1/clients/{id}

---

## Client Details

GET

/api/v1/clients/{id}

---

# CEO Agent APIs

## Submit Directive

POST

/api/v1/ceo/directive

Purpose

Starts a new workflow.

Example

"I own a restaurant and need more online customers."

Returns

Workflow ID

---

## Current Thought

GET

/api/v1/ceo/thought

Returns

Current CEO reasoning

---

## Workflow Status

GET

/api/v1/ceo/workflow/{id}

Returns

Workflow progress

Task Queue

Status

ETA

---

## Live Stream

GET

/api/v1/ceo/stream

Server Sent Events

Updates

Thoughts

Tasks

Workflow

Confidence

---

## Cancel Workflow

POST

/api/v1/ceo/workflow/{id}/cancel

---

## Retry Workflow

POST

/api/v1/ceo/workflow/{id}/retry

---

# Agent APIs

## Get Agents

GET

/api/v1/agents

---

## Agent Details

GET

/api/v1/agents/{id}

---

## Agent Health

GET

/api/v1/agents/health

---

## Agent Logs

GET

/api/v1/agents/{id}/logs

---

## Restart Agent

POST

/api/v1/agents/{id}/restart

---

# Workflow APIs

## List Workflows

GET

/api/v1/workflows

---

## Workflow Details

GET

/api/v1/workflows/{id}

---

## Workflow Timeline

GET

/api/v1/workflows/{id}/events

---

## Workflow Tasks

GET

/api/v1/workflows/{id}/tasks

---

# Reports APIs

## Executive Report

GET

/api/v1/reports/{workflowId}

---

## Export PDF

GET

/api/v1/reports/{workflowId}/pdf

---

## Download JSON

GET

/api/v1/reports/{workflowId}/json

---

# Dashboard APIs

## Dashboard Overview

GET

/api/v1/dashboard

Returns

Organizations

Clients

Agents

Running Tasks

Reports

Notifications

---

## Recent Activities

GET

/api/v1/dashboard/activity

---

## Metrics

GET

/api/v1/dashboard/metrics

---

# Notification APIs

GET

/api/v1/notifications

PUT

/api/v1/notifications/{id}/read

DELETE

/api/v1/notifications/{id}

---

# Settings APIs

GET

/api/v1/settings

PUT

/api/v1/settings

---

# Search APIs

GET

/api/v1/search

Supports

Clients

Reports

Workflows

Agents

Organizations

---

# Upload APIs

POST

/api/v1/upload

Supports

PDF

Images

Excel

CSV

Documents

---

# API Security

JWT Required

HTTPS Only

Rate Limiting

Input Validation

Request Logging

Role-Based Authorization

SQL Injection Protection

XSS Protection

CSRF Protection

---

# Error Codes

200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error

503 Service Unavailable

---

# Rate Limits

Authenticated

100 Requests / Minute

Guest

20 Requests / Minute

Admin

Unlimited (Configurable)

---

# API Logging

Every request logs

Request ID

User ID

Organization ID

Endpoint

Method

Status

Execution Time

Timestamp

---

# API Versioning

Current

v1

Future

v2

v3

Older versions remain backward compatible.

---

# Success Criteria

The API Layer should

Support all frontend features

Secure all endpoints

Support enterprise scaling

Provide consistent responses

Be fully documented

Be easy to extend

Remain backward compatible