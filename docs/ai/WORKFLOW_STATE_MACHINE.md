# StrtOS - Workflow State Machine

Version: 1.0.0

Status: Development Ready

Component: Workflow State Machine

---

# Purpose

This document defines the lifecycle of every workflow executed inside StrtOS.

Every workflow must follow the same state machine.

This document is the single source of truth for workflow execution.

---

# Workflow Overview

User Request

↓

Workflow Created

↓

Planning

↓

Agent Assignment

↓

Execution

↓

Validation

↓

Executive Report

↓

Completed

---

# State Definitions

Every workflow can only exist in one state at a time.

States are immutable.

Transitions are controlled by the CEO Agent.

---

# State 1

CREATED

Description

Workflow has been created.

Allowed Actions

Initialize workflow

Generate Workflow ID

Store request

Create event

Next State

PLANNING

---

# State 2

PLANNING

CEO analyzes

Business Goal

Industry

Priority

Workflow

Dependencies

Output

Execution Plan

Next State

AGENT_ASSIGNMENT

---

# State 3

AGENT_ASSIGNMENT

CEO selects

Business Agent

SEO Agent

Marketing Agent

Campaign Agent

Analytics Agent

Output

Task Queue

Next State

READY

---

# State 4

READY

Workflow waiting for execution.

Allowed

Start

Cancel

Timeout

---

# State 5

RUNNING

Workflow is executing.

Tasks

Sequential

Parallel

Conditional

Dashboard

Live Updates

---

# State 6

WAITING

Workflow waiting for

Agent

Tool

API

Memory

Human Approval (Future)

Timeout

Resume

---

# State 7

VALIDATING

CEO validates

Reports

Confidence

Schema

Business Rules

Output

Validation Result

---

# State 8

REPORTING

CEO merges

Business Report

SEO Report

Marketing Report

Analytics Report

Generate Executive Report

---

# State 9

COMPLETED

Workflow Finished.

Store

Memory

Events

Analytics

Reports

Metrics

---

# Failure States

FAILED

One or more critical failures.

Retry possible.

---

CANCELLED

User cancelled workflow.

---

TIMEOUT

Workflow exceeded execution time.

---

RETRYING

Retry in progress.

---

PAUSED

Workflow paused.

Future Feature.

---

# Transition Table

CREATED

↓

PLANNING

↓

AGENT_ASSIGNMENT

↓

READY

↓

RUNNING

↓

VALIDATING

↓

REPORTING

↓

COMPLETED

---

# Retry Flow

RUNNING

↓

FAILED

↓

RETRYING

↓

RUNNING

↓

COMPLETED

OR

FAILED

---

# Timeout Flow

RUNNING

↓

TIMEOUT

↓

Retry

↓

Resume

↓

FAILED

---

# Cancellation Flow

RUNNING

↓

CANCELLED

↓

Cleanup

↓

Archive

---

# Parallel Execution

Allowed

Business Agent

SEO Agent

Competitor Agent

Opportunity Agent

Analytics Agent

Can execute together.

---

# Sequential Execution

Must execute

Marketing Strategy

↓

Campaign Planning

↓

Report Generator

---

# State Events

Every transition publishes an event.

Workflow Created

Workflow Started

Planning Started

Planning Completed

Task Assigned

Task Started

Task Completed

Validation Started

Validation Passed

Validation Failed

Workflow Finished

---

# State Persistence

Every transition stored in database.

workflow_events

Stores

Previous State

Current State

Timestamp

Workflow ID

Agent

Metadata

---

# State Recovery

If server crashes

Restore

Workflow State

Task Queue

Memory

Current Agent

Resume execution.

---

# Dashboard Mapping

CREATED

Gray

PLANNING

Blue

RUNNING

Orange

VALIDATING

Purple

COMPLETED

Green

FAILED

Red

WAITING

Yellow

---

# State Rules

Only CEO changes workflow state.

Agents cannot modify workflow state.

Every transition is logged.

Every transition is validated.

No illegal transitions allowed.

---

# Illegal Transitions

CREATED

×

COMPLETED

RUNNING

×

CREATED

FAILED

×

PLANNING

Only valid transitions allowed.

---

# Performance Targets

Workflow Creation

<100ms

Planning

<500ms

Assignment

<300ms

Validation

<500ms

Completion

Real Time

---

# Future States

HUMAN_APPROVAL

MODEL_SWITCH

SELF_EVALUATION

AI_REVIEW

KNOWLEDGE_UPDATE

AUTO_OPTIMIZATION

---

# Success Criteria

Workflow State Machine is successful when

Every workflow follows valid transitions

Recovery works

Retries work

Dashboard updates correctly

LangGraph maps directly

No invalid state transitions occur