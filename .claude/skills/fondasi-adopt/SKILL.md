---
name: fondasi-adopt
description: Bring any Arumi Studios repository (new or existing, any stack) onto the Fondasi base — read the repo, audit it against Fondasi's rules (conventions, Indonesian for users, web baseline, UI, feedback, settings/storage, server contract, shared data, visual assets), write docs/fondasi-audit.md, interview the user for app-specific decisions, and set up CLAUDE.md, AGENTS.md, hooks, CI, progress and decisions from the templates. Use when the user asks to audit or review a repo against Fondasi, to adopt Fondasi, or starts work in a repo that has no Fondasi pointer yet.
---

# Adopt Fondasi

Follow `docs/adopting.md` in Fondasi: read → audit → ask → set up the base → plan.

- Fondasi is the base, not the design of the app: copy rules and templates, never another app's own choices.
- Audit first, change nothing until the user agrees; report in `docs/fondasi-audit.md` (table: area, rule, status
  ok/partial/missing/n/a + reason, evidence file:line, fix, effort S/M/L), with the Fondasi commit it was checked against.
- Ask only what the repository cannot answer, a few questions at a time; record answers as the app's `D-…` decisions.
- Base setup in small PRs from `templates/repo/` (and `templates/ai/` when visuals are needed); keep what the repo
  already has; leave app-specific sections as placeholders for the user to decide.
- End with ordered next steps in the app's `docs/progress.md`; the user chooses the order of the fixes.
