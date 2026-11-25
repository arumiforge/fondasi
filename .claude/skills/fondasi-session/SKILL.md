---
name: fondasi-session
description: Start and end every Fondasi work session the same way across Claude accounts — sync, git identity, read docs/progress.md, claim a branch, hand off by updating progress.md. Use at the start of every session in arumiforge/fondasi and before ending one.
---

# Fondasi session

Repositories are the only shared memory between Claude accounts.

## Start

1. `git fetch origin && git status && git log --oneline -5 origin/main`
2. Identity and hooks: `git config user.name "${ARUMI_GIT_NAME:-Arumi Studios}"`,
   `git config user.email "${ARUMI_GIT_EMAIL:-arumiforge@gmail.com}"`, `git config core.hooksPath .githooks`.
3. Read `CLAUDE.md` → `docs/progress.md` → the last entries of `docs/decisions.md`.
4. Claim work in *Active work* of `progress.md` (branch, neutral session label such as `$ARUMI_ACCOUNT`, task).
5. `tools/data-check` must pass before you change data.

## End

Update `docs/progress.md` (active work, next steps, blockers, one session-log line; keep 10), `CHANGELOG.md`,
commit (no AI attribution), push, open or update the PR. Never write emails, names, IPs or tokens into the repo.
