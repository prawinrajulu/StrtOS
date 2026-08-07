# StrtOS - React Component Architecture

Version: 1.0.0

Status: Development Ready

Owner: Frontend Team

Priority: Critical

---

# Purpose

This document defines the complete frontend architecture of StrtOS.

The frontend must be

- Modular
- Component Based
- Scalable
- Maintainable
- Enterprise Ready

Every page must follow this architecture.

---

# Technology Stack

React 19

TypeScript

TailwindCSS

React Flow

Framer Motion

TanStack Query

React Router

Zustand

React Hook Form

Zod

---

# Folder Structure

frontend/

src/

app/

pages/

components/

layouts/

hooks/

services/

store/

types/

utils/

constants/

assets/

styles/

contexts/

providers/

router/

---

# App Structure

App

↓

Auth Provider

↓

Theme Provider

↓

Query Provider

↓

Router

↓

Dashboard Layout

↓

Pages

---

# Layout Components

AppLayout

Sidebar

Topbar

PageContainer

Footer

FloatingAssistant

NotificationCenter

---

# Shared Components

GlassCard

Button

Input

Select

Modal

Dialog

Toast

Loader

EmptyState

Badge

Tooltip

Avatar

Dropdown

Table

Pagination

SearchBox

StatusChip

---

# Dashboard Components

DashboardHeader

MetricsGrid

WorkflowGraph

AgentGrid

TaskQueue

Timeline

ConfidenceRing

ActivityFeed

QuickActions

ExecutiveSummary

---

# CEO Components

CEOThoughtPanel

WorkflowPlanner

DecisionCard

AgentAssignments

ExecutionTimeline

ConfidenceAnalysis

RiskAnalysis

RecommendationPanel

---

# Client Components

ClientTable

ClientCard

ClientDetails

ClientForm

ClientHistory

BusinessProfile

---

# Workflow Components

WorkflowCanvas

WorkflowStatus

WorkflowTimeline

WorkflowHistory

WorkflowMetrics

WorkflowEvents

---

# Agent Components

AgentCard

AgentHealth

AgentStatus

AgentLogs

AgentMetrics

AgentConfiguration

---

# Report Components

ExecutiveReport

BusinessReport

SEOReport

CompetitorReport

MarketingReport

CampaignReport

AnalyticsReport

ExportPDF

---

# Settings Components

ProfileSettings

OrganizationSettings

AISettings

ModelSettings

NotificationSettings

SecuritySettings

BillingSettings

---

# State Management

Global

Authentication

Organization

Theme

Notifications

Workflow

Current User

Local

Forms

Filters

Dialogs

Search

Pagination

---

# API Layer

services/

auth.service.ts

client.service.ts

workflow.service.ts

ceo.service.ts

agent.service.ts

dashboard.service.ts

report.service.ts

settings.service.ts

---

# Hooks

useWorkflow

useDashboard

useCEO

useAgents

useClients

useReports

useNotifications

---

# Routing

/

↓

Login

/dashboard

/clients

/workflows

/agents

/reports

/settings

/profile

---

# UI Rules

Glassmorphism

Rounded Cards

Consistent Spacing

Reusable Components

Dark Theme First

Minimal Design

Smooth Animations

Responsive

---

# Animation Rules

Framer Motion

Page Transitions

Fade

Slide

Scale

Hover

Loading Skeletons

---

# Error Handling

Network Errors

Validation Errors

Loading States

Empty States

Retry Actions

---

# Responsive Design

Desktop

Laptop

Tablet

Mobile

---

# Accessibility

Keyboard Navigation

ARIA Labels

Screen Reader Support

Focus Management

Color Contrast

---

# Performance

Lazy Loading

Code Splitting

Memoization

Virtual Lists

Image Optimization

React Query Cache

---

# Success Criteria

Frontend is complete when

Component tree is modular

Pages are reusable

State management is clean

Performance is optimized

UI is responsive

Dashboard updates in real time

Matches StrtOS Design System