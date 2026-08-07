# StrtOS - FastAPI Backend Structure

Version: 1.0.0

Status: Development Ready

Owner: Backend Team

Priority: Critical

---

# Purpose

This document defines the backend architecture of StrtOS.

Every backend developer must follow this structure.

No feature should be implemented outside this architecture.

---

# Technology Stack

FastAPI

Python 3.12+

Pydantic v2

SQLAlchemy

Alembic

PostgreSQL

Redis

LangGraph

JWT

Server Sent Events

Docker

---

# Project Structure

backend/

app/

main.py

config.py

dependencies.py

database.py

middleware.py

exceptions.py

logging.py

core/

api/

v1/

auth.py

clients.py

ceo.py

agents.py

reports.py

dashboard.py

workflows.py

settings.py

services/

repositories/

models/

schemas/

ceo/

agents/

execution/

graph/

memory/

events/

tools/

utils/

tests/

---

# Entry Point

main.py

Responsibilities

Initialize FastAPI

Load Config

Connect Database

Connect Redis

Register Middleware

Register Routes

Register Event System

Start Server

---

# API Layer

Responsibilities

Receive HTTP Requests

Validate Request

Call Service Layer

Return Response

Never write business logic.

---

# Service Layer

Responsibilities

Business Logic

Workflow Logic

CEO Logic

Agent Logic

Validation

Transactions

---

# Repository Layer

Responsibilities

Database Access

CRUD

Transactions

Queries

No business logic.

---

# Model Layer

SQLAlchemy Models

Organization

User

Client

Workflow

Task

Agent

Memory

Reports

Events

Notifications

---

# Schema Layer

Pydantic

Request Models

Response Models

Validation Models

DTO

---

# CEO Module

Contains

Orchestrator

Decision Engine

Workflow Engine

Intent Engine

Task Planner

Validator

Reporter

---

# Agent Module

Contains

Business Agent

SEO Agent

Competitor Agent

Marketing Agent

Campaign Agent

Analytics Agent

Report Generator

---

# Execution Module

Contains

Scheduler

Retry Manager

Validator

Health Monitor

Execution Engine

---

# Graph Module

Contains

State

Nodes

Edges

Builder

Executor

Checkpoint

---

# Memory Module

Contains

Working Memory

Conversation Memory

Business Memory

Long Term Memory

Knowledge Memory

---

# Tool Module

Contains

Google Tools

SEO Tools

Marketing Tools

Analytics Tools

Storage

Authentication

Tool Registry

---

# Event Module

Contains

Publisher

Subscriber

Redis Streams

SSE

Notifications

---

# Utils

Logging

DateTime

Helpers

Constants

Enums

Validators

---

# Middleware

JWT

Logging

Rate Limiting

CORS

Compression

Security Headers

---

# Exception Handling

ValidationException

WorkflowException

MemoryException

DatabaseException

AuthenticationException

AuthorizationException

ToolException

ModelException

---

# Dependency Injection

Use FastAPI Depends()

Inject

Database

Redis

Current User

Repositories

Services

Configuration

---

# Configuration

Environment Variables

Database URL

Redis URL

JWT Secret

API Keys

Model Keys

Storage Keys

---

# Logging

Every request logs

Request ID

User

Organization

Endpoint

Execution Time

Errors

---

# Background Tasks

Workflow Cleanup

Memory Cleanup

Health Checks

Notifications

Backups

---

# Startup Tasks

Database

Redis

Tool Registry

Agent Registry

LangGraph

Event Bus

---

# Shutdown Tasks

Close Database

Close Redis

Save State

Flush Logs

---

# Coding Standards

PEP8

Type Hints

Docstrings

SOLID Principles

Dependency Injection

Repository Pattern

Service Pattern

---

# Performance

Async Endpoints

Connection Pooling

Redis Cache

Database Indexes

Background Workers

Streaming

---

# Security

JWT

HTTPS

RBAC

Secrets Manager

Audit Logs

Prepared Statements

---

# Success Criteria

Backend is complete when

Folder structure followed

Services separated

Repositories separated

No business logic in controllers

Fully async

Scalable

Production Ready