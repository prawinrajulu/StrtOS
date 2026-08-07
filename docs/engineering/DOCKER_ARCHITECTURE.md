# StrtOS - Docker Architecture

Version: 1.0.0

Status: Development Ready

Owner: DevOps Team

Priority: Critical

---

# Purpose

This document defines the Docker architecture for StrtOS.

Every service runs inside its own container.

Containers communicate through Docker Network.

---

# Goals

Isolation

Scalability

Portability

Reproducibility

Easy Deployment

Production Ready

---

# Technology

Docker

Docker Compose

Nginx

FastAPI

React

PostgreSQL

Redis

Prometheus

Grafana

---

# Container Architecture

                 Internet

                     │

                     ▼

                 Nginx Reverse Proxy

              ┌──────────────┐

              ▼              ▼

      React Frontend      FastAPI Backend

                               │

          ┌────────────┬─────────────┐

          ▼            ▼             ▼

     PostgreSQL      Redis      AI Models

---

# Services

frontend

backend

postgres

redis

nginx

prometheus

grafana

future-worker

future-celery

future-rabbitmq

---

# Docker Network

Network Name

strtos-network

All containers communicate internally.

No direct database exposure.

---

# Frontend Container

Image

Node

Responsibilities

React Build

Serve Static Files

API Communication

---

# Backend Container

Image

Python

Responsibilities

FastAPI

LangGraph

CEO Agent

Specialist Agents

Workflow Engine

---

# PostgreSQL Container

Stores

Organizations

Users

Clients

Workflows

Tasks

Reports

Memory

Audit Logs

---

# Redis Container

Stores

Pub/Sub

Workflow Events

Dashboard Events

Agent Events

Caching

---

# Nginx Container

Responsibilities

Reverse Proxy

SSL

Compression

Security Headers

Load Balancing

---

# Monitoring

Prometheus

Collect Metrics

Grafana

Visualize Metrics

---

# Environment Variables

Backend

DATABASE_URL

REDIS_URL

JWT_SECRET

GOOGLE_API_KEY

OPENROUTER_API_KEY

LOG_LEVEL

---

Frontend

VITE_API_URL

VITE_APP_NAME

VITE_ENV

---

Database

POSTGRES_USER

POSTGRES_PASSWORD

POSTGRES_DB

---

Redis

REDIS_PORT

REDIS_PASSWORD

---

# Docker Volumes

postgres_data

redis_data

logs

uploads

backups

---

# Docker Compose Services

frontend

backend

postgres

redis

nginx

grafana

prometheus

---

# Health Checks

Backend

/api/health

Frontend

/

Database

SELECT 1

Redis

PING

---

# Logging

Container Logs

Application Logs

Workflow Logs

AI Logs

API Logs

---

# Security

Run as Non-root User

Read-only Filesystem

Secrets via Environment Variables

No Hardcoded Credentials

Private Docker Network

---

# Scaling

Frontend

Multiple Replicas

Backend

Multiple Replicas

Redis

Cluster (Future)

Database

Primary + Read Replica (Future)

---

# Production Deployment

Frontend

Vercel OR Docker

Backend

AWS EC2 Docker

Database

AWS RDS PostgreSQL

Redis

AWS ElastiCache

Monitoring

Grafana Cloud

---

# Backup

Database

Daily

Uploads

Daily

Configuration

Git

---

# CI/CD

GitHub Push

↓

GitHub Actions

↓

Run Tests

↓

Build Images

↓

Push Docker Images

↓

Deploy

---

# Future

Kubernetes

Auto Scaling

Service Mesh

Multi Region

Blue Green Deployment

Canary Releases

---

# Success Criteria

Docker Architecture is complete when

All services start successfully

Containers communicate correctly

Health checks pass

Scaling is supported

Production deployment is reliable