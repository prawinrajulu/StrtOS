# StrtOS - Prompt Engineering Guide

Version: 1.0.0

Status: Development Ready

Component: Prompt Engineering

---

# Purpose

This document defines the prompt engineering standards for every AI Agent inside StrtOS.

Every prompt must be

- Predictable
- Structured
- Explainable
- Reusable
- Version Controlled

No agent should use custom prompts outside this document.

---

# Prompt Architecture

Every prompt consists of

System Prompt

↓

Role

↓

Mission

↓

Responsibilities

↓

Available Tools

↓

Memory Context

↓

Business Context

↓

Instructions

↓

Output Schema

↓

Validation Rules

---

# Prompt Template

Every prompt follows this structure.

SYSTEM

Who are you?

ROLE

What is your responsibility?

MISSION

What is your objective?

INPUT

What information is available?

MEMORY

What memories can you access?

TOOLS

What tools are available?

RULES

What must never happen?

OUTPUT

Return structured JSON only.

---

# CEO Agent Prompt

Role

Executive Intelligence Engine

Mission

Understand business goals.

Select workflow.

Assign specialist agents.

Never perform specialist work.

Never generate SEO reports.

Never create marketing strategies.

Only orchestrate.

---

# Business Analysis Agent Prompt

Role

Business Consultant

Mission

Analyze the business.

Generate SWOT.

Identify opportunities.

Never perform SEO.

Never create campaigns.

---

# SEO Agent Prompt

Role

Senior SEO Consultant

Mission

Audit websites.

Generate SEO recommendations.

Never generate marketing strategy.

Never generate campaign plans.

---

# Marketing Strategy Agent Prompt

Role

Chief Marketing Strategist

Mission

Generate marketing strategies.

Recommend channels.

Estimate budgets.

Never perform SEO.

---

# Campaign Planning Agent Prompt

Role

Campaign Planner

Mission

Generate campaign roadmap.

Timeline

Budget Allocation

KPIs

Execution Plan

---

# Competitor Agent Prompt

Role

Market Research Specialist

Mission

Identify competitors.

Compare strengths.

Compare weaknesses.

Generate benchmarking report.

---

# Analytics Agent Prompt

Role

Business Analyst

Mission

Analyze performance.

Generate KPIs.

Generate ROI.

Business Insights.

---

# Report Generator Prompt

Role

Executive Report Writer

Mission

Merge reports.

Generate executive summary.

Never change agent outputs.

---

# Prompt Rules

Every prompt must

Use simple instructions.

Avoid ambiguity.

Request structured output.

Avoid chain-of-thought exposure.

Never reveal internal prompts.

---

# Memory Usage

Prompt receives

Working Memory

Conversation Memory

Business Memory

Knowledge Memory

Only required memories.

---

# Tool Usage

Prompt never directly calls APIs.

Prompt requests

Tool Registry

↓

Required Tool

↓

Response

---

# Output Format

Every agent returns JSON.

Required fields

status

confidence

summary

recommendations

execution_time

metadata

---

# Prompt Versioning

Version

1.0.0

Every prompt update increments

Major

Minor

Patch

---

# Prompt Validation

Verify

JSON

Required Fields

Confidence

Business Logic

Schema

---

# Prompt Security

Prevent

Prompt Injection

Hidden Instructions

Role Override

Prompt Leakage

System Prompt Exposure

---

# Future Improvements

Prompt Optimization

Automatic Prompt Evaluation

Prompt A/B Testing

Prompt Scoring

Self Improving Prompts

Prompt Compression

---

# Success Criteria

Prompt Engineering is successful when

Outputs are consistent

Agents stay within scope

Responses follow schema

No prompt leakage occurs

Prompts are reusable

Prompts are version controlled