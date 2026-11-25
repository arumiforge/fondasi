---
name: app-session
description: Start and end every work session in this repository the same way across Claude accounts — sync, git identity, environment, read CLAUDE.md and docs/progress.md, claim a branch, keep tasks and decisions, hand off by updating progress.md. Use at the start of every session and before ending one (or when the context is getting long). Rename to <app>-session when planting it.
---

# Session start and handoff

Follows Fondasi `docs/agent-workflow.md`; adapt the environment step to this repository with the user.

## Start
1. `git fetch origin && git status && git log --oneline -5 origin/main`
2. `git config user.name "Arumi Studios"`, `git config user.email "arumiforge@gmail.com"`, `git config core.hooksPath .githooks`
3. Environment: <dependencies, services to start — fill in for this repository>
4. Read `CLAUDE.md` → `docs/progress.md` → latest `docs/interview/` round → last entries of `docs/decisions.md`.
5. Claim work in *Active work* (branch, neutral session label, task, status); never use another session's branch.
6. Tell the user where things stand and what you will do.

## During
- Task list for multi-step work; decisions recorded as they happen; ask the user for choices that are theirs.
- Commit small, push often, PRs never merged without the user; verify (tests, lint, build, screenshots) before claiming done.

## End
Update `docs/progress.md` (status, next steps, blockers, one session-log line, keep 10), decisions, `CHANGELOG.md`;
commit, push, open/update the PR. No emails, names, IPs or tokens in the repository.
