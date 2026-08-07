# StrtOS - Coding Standards

Version: 1.0.0

Status: Production Ready

Owner: Engineering Team

Priority: Critical

---

# Purpose

This document defines the coding standards for StrtOS.

Every developer must follow these standards.

Code consistency is more important than personal coding style.

---

# General Principles

Write clean code.

Write readable code.

Write maintainable code.

Write testable code.

Write scalable code.

Always prefer clarity over cleverness.

---

# Architecture Principles

Follow

SOLID Principles

DRY (Don't Repeat Yourself)

KISS (Keep It Simple)

YAGNI (You Aren't Gonna Need It)

Separation of Concerns

Dependency Injection

Repository Pattern

Service Pattern

---

# Python Standards

Python Version

3.12+

PEP8

Mandatory

Maximum Line Length

100 Characters

Indentation

4 Spaces

Type Hints

Required

Docstrings

Required

Async

Use async/await wherever applicable.

---

# FastAPI Standards

Controllers

Only receive requests.

No business logic.

Services

Business logic only.

Repositories

Database operations only.

Schemas

Validation only.

---

# React Standards

Use Functional Components.

Never use Class Components.

Use Hooks.

Use TypeScript.

Keep components reusable.

Avoid prop drilling.

Use Zustand for global state.

---

# Folder Naming

Use

snake_case

Python

Use

PascalCase

React Components

Use

camelCase

Variables

---

# File Naming

Python

business_agent.py

React

BusinessCard.tsx

Styles

dashboard.css

---

# Variable Naming

Good

client_name

workflow_status

execution_time

Bad

x

temp

abc

data1

---

# Function Naming

Use verbs.

Examples

createWorkflow()

calculateConfidence()

generateReport()

validateInput()

publishEvent()

---

# Class Naming

PascalCase

CEOOrchestrator

BusinessAgent

WorkflowEngine

MemoryManager

EventPublisher

---

# Constants

UPPER_CASE

MAX_RETRIES

DEFAULT_TIMEOUT

API_VERSION

---

# Enums

Use Enums instead of strings.

WorkflowStatus

AgentStatus

Priority

Role

MemoryType

---

# Error Handling

Never ignore exceptions.

Catch specific exceptions.

Log every error.

Return meaningful messages.

Never expose internal stack traces.

---

# Logging

Log

Workflow Start

Workflow Finish

Errors

Retries

Agent Execution

Tool Usage

Model Selection

---

# Comments

Write comments only when necessary.

Bad

# Increment i

i += 1

Good

Explain business logic.

---

# Git Standards

Branch

feature/business-agent

bugfix/workflow

hotfix/security

---

# Commit Messages

Format

type(scope): description

Examples

feat(ceo): add workflow planner

fix(api): resolve validation issue

docs(ai): update prompt library

refactor(memory): optimize cache loading

---

# Pull Requests

Must include

Description

Screenshots (Frontend)

Test Results

Checklist

Reviewer

---

# Code Review Checklist

Readable

Typed

Tested

Documented

Secure

No duplicated code

No hardcoded secrets

No debug logs

---

# Security Rules

Never commit

.env

API Keys

Passwords

Tokens

Certificates

Always use environment variables.

---

# Testing Standards

Every feature requires

Unit Tests

Integration Tests

API Tests

AI Validation Tests

---

# Performance

Avoid N+1 Queries

Use Async

Cache Expensive Operations

Optimize Database Queries

Reuse Connections

---

# AI Coding Rules

Agents must never

Call APIs directly

Access database directly

Modify another agent's memory

Ignore CEO instructions

Bypass Tool Registry

---

# Documentation

Every public function

Must contain

Purpose

Parameters

Return Value

Exceptions

Example Usage

---

# Code Quality

Use Ruff

Use Black

Use MyPy

Use Pytest

Run all checks before commit.

---

# CI Rules

Every Pull Request must pass

Lint

Formatting

Type Checking

Tests

Security Scan

Docker Build

---

# Definition of Done

A feature is complete only if

Code Implemented

Reviewed

Tested

Documented

Performance Verified

Security Verified

Merged Successfully

---

# Success Criteria

The codebase is successful when

Consistent coding style

Minimal technical debt

Easy onboarding for new developers

High maintainability

Enterprise-ready quality