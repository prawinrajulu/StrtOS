# StrtOS - Redis Event System

Version: 1.0.0

Status: Development Ready

Owner: Backend Engineering Team

Priority: Critical

---

# Purpose

This document defines the real-time event architecture of StrtOS.

Redis acts as the Event Bus between

- CEO Agent
- Specialist Agents
- Dashboard
- Notifications
- Workflow Engine

Redis enables live updates without polling.

---

# Technology

Redis

Redis Pub/Sub

Redis Streams

Server Sent Events

FastAPI

AsyncIO

---

# Architecture

                    CEO Agent

                        │

                        ▼

                  Redis Event Bus

        ┌─────────┬─────────┬─────────┐

        ▼         ▼         ▼

   Dashboard    Agents    Notifications

---

# Why Redis?

Benefits

Ultra Fast

In Memory

Supports Pub/Sub

Supports Streams

Scalable

Low Latency

Reliable

---

# Event Types

Workflow Events

Agent Events

Task Events

Dashboard Events

Notification Events

Memory Events

Audit Events

---

# Workflow Events

workflow.created

workflow.started

workflow.planning

workflow.running

workflow.validating

workflow.completed

workflow.failed

workflow.cancelled

workflow.retry

---

# Task Events

task.created

task.assigned

task.started

task.completed

task.failed

task.retry

task.cancelled

---

# Agent Events

agent.online

agent.offline

agent.busy

agent.completed

agent.failed

agent.retry

health.updated

---

# Dashboard Events

dashboard.refresh

dashboard.metrics

dashboard.timeline

dashboard.graph

dashboard.notifications

dashboard.thought

---

# Notification Events

notification.created

notification.read

notification.deleted

---

# Event Format

Every event contains

event_id

workflow_id

task_id

agent_id

event_name

status

timestamp

payload

metadata

---

# Example Event

{
  "event_id":"evt_001",
  "workflow_id":"wf_001",
  "agent_id":"seo_agent",
  "event_name":"task.completed",
  "status":"success",
  "timestamp":"2026-08-07T10:30:00Z",
  "payload":{},
  "metadata":{}
}

---

# Redis Channels

workflow.events

task.events

agent.events

dashboard.events

notification.events

memory.events

audit.events

---

# Event Flow

CEO

↓

Redis Publish

↓

Dashboard

↓

Frontend Updates

---

# Publish Example

CEO Agent

↓

workflow.started

↓

Redis

↓

Dashboard

↓

Workflow Graph Updates

---

# Subscribe Example

Dashboard

↓

Subscribe

↓

workflow.events

↓

Receive Updates

↓

Render UI

---

# Redis Streams

Used For

Workflow History

Audit Logs

Replay Events

Recovery

Monitoring

---

# Event Persistence

Short-Term

Redis

Long-Term

PostgreSQL

---

# Event Priority

Critical

Workflow

High

Agent

Medium

Dashboard

Low

Analytics

---

# Retry Policy

Publish Failed

↓

Retry

↓

Log Error

↓

Continue Workflow

---

# Health Monitoring

Monitor

Redis Connection

Latency

Memory Usage

Subscribers

Failed Events

Queue Length

---

# Event Security

JWT Authentication

Encrypted Channels

Organization Isolation

Audit Logging

Validation

---

# Performance Goals

Publish

<10ms

Subscribe

<10ms

Dashboard Update

<100ms

Agent Notification

Real Time

---

# Future Enhancements

Redis Cluster

Kafka Integration

RabbitMQ Support

Distributed Event Bus

Event Replay

Dead Letter Queue

Priority Queues

---

# Success Criteria

Redis Event System is complete when

Events publish successfully

Dashboard updates instantly

Workflow graph updates live

Notifications work

Agent communication is real-time

No event loss

Supports horizontal scaling