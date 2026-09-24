---
layout: default
date: "2026-09-24"
title: Checklist — AI Team Connectors and APIs
description: "Least-privilege connector checklist for Gmail, Calendar, Drive, store APIs, and remote tools."
tags: ["ai", "checklist", "api", "security"]
---

<h1 align="center">Checklist: Connectors and APIs</h1>

Wiring beats chat. Connect once, scope tightly, keep humans on the send button.

## Before you connect anything

- [ ] Name the workflow (e.g. “draft client replies from labeled threads”)
- [ ] List the minimum scopes (read mail vs send; calendar free/busy vs create events)
- [ ] Decide who may approve outbound messages
- [ ] Store API keys/secrets in a vault or the bot’s secret store — never in chat history or a public repo

## Typical connectors

- [ ] **Email** — search and draft; send only after human approval
- [ ] **Calendar** — reminders and availability; no surprise meetings without a rule
- [ ] **Drive / docs** — create intake PDFs and shared drafts in a known folder
- [ ] **Store / admin APIs** — read sales or tax data; write only with an explicit playbook
- [ ] **RMM / remote** — inventory and ticket notes; never auto-run destructive scripts from a chat prompt

## Hygiene

- [ ] Separate production keys from sandbox keys
- [ ] Rotate keys when a bot or person leaves the workflow
- [ ] Log which bot used which connector for sensitive actions
- [ ] Quarterly review: disconnect unused apps

Back to: [AI chief of staff article](/blog/ai-chief-of-staff-msp) · [Roles checklist](/blog/checklist-ai-team-roles) · [First week](/blog/checklist-ai-team-first-week)
