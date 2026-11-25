# How agents work in every repository (F-017)

Claude sessions (and Codex) work across several accounts that share nothing but the repositories. These rules make
any session in any repository start, work and hand off the same way. Each repository plants them as its own session
skill from [`templates/repo/.claude/skills/app-session/SKILL.md`](../templates/repo/.claude/skills/app-session/SKILL.md)
(renamed `<app>-session`, e.g. SPMB's `spmb-session`), adapted with the user.

## The repository is the memory

| File | Holds | Who writes |
| --- | --- | --- |
| `CLAUDE.md` | What the app is, stack, commands, rules, Fondasi pointer | the session with the user, when rules change |
| `AGENTS.md` | Scope and git rules for Codex and other agents | same |
| `docs/progress.md` | Current phase, active work (branch, session label, task, status), next steps, blockers, session log (last 10) | every session: read first, update last |
| `docs/decisions.md` | Decisions `D-…` with status, context, decision, consequences | when a decision is made, not at the end |
| `docs/interview/` (optional) | Open questions and the user's answers, one file per round | the interviewing session |
| `CHANGELOG.md` | User-visible changes | with the work |

Never write emails, names of people, IPs, tokens or passwords into these files; use neutral session labels
(`akun-1`, `session ui-round`).

## Session start

1. Sync: `git fetch origin`, `git status`, recent `origin/main` log.
2. Identity and hooks: `Arumi Studios <arumiforge@gmail.com>`, `git config core.hooksPath .githooks`.
3. Environment: dependencies installed, services running (database, etc.) as the repo's cloud-environment page says.
4. Read in order: `CLAUDE.md` → `docs/progress.md` → the latest interview round → the last decisions → the Fondasi
   docs the task touches.
5. Claim work: a row in *Active work*; never commit to a branch another session claimed; use the branch this
   session was given or create one from `origin/main`.
6. Tell the user in one or two lines where things stand and what will happen next.

## During the session

- **Tasks**: for work with three or more steps, keep a task list (the session's task tool) and mark each step as it
  starts and ends; the list is for this session — anything the next session needs goes into `progress.md`.
- **Decisions**: ask the user when a choice is theirs (purpose, users, clients, money, legal, look and feel); a few
  questions at a time with a recommended option; record the answer as a decision immediately.
- **Context**: read only the part of a file you need; search before reading; keep long outputs out of the chat
  (write them to files); when the conversation grows long, update `progress.md` early so a fresh session can continue.
- **Small, pushed steps**: commit small, push often (containers can be reclaimed), one PR per coherent change,
  checks green before asking for a merge. Agents never merge unless the user asks.
- **Verify before claiming**: run the tests, lint, build; for UI, screenshots at 360 and 1280 px; say plainly what was
  not tested.
- **Fondasi first**: when a rule exists in Fondasi, follow it; when a new rule would help other apps, propose it for
  Fondasi instead of only writing it locally.

## Session end (or when the context is getting long)

1. `docs/progress.md`: phase, active-work row status, next steps (concrete, ordered, startable without chat history),
   blockers, one session-log line (date · label · branch — what was done; next).
2. Decisions, `CHANGELOG.md`, docs touched by the change.
3. Commit, push, open or update the PR; tell the user what is waiting for them.

## Several sessions in parallel (coordinator and workers)

For a large round, one **coordinator** session owns an integration branch and the shared files; **workers** run as
separate sessions on their own branches:

1. The coordinator lands everything shared first (folders, migrations of shared tables, permission keys, settings
   defaults, menu entries, the round plan with each worker's files and interfaces).
2. Workers branch from the integration branch, touch only their own files, open one PR into it, and never edit
   `progress.md`, `decisions.md` or `CHANGELOG.md` — they put proposed decisions and notes in the PR description.
3. The coordinator reviews, runs the checks, merges into the integration branch, updates the shared docs and opens
   one PR into `main` for the user.

Proven in SPMB (`docs/coordination.md` there).

## Codex and other agents

Codex follows `AGENTS.md` and works only from briefs in the repository ([visual-assets.md](visual-assets.md)). The
same commit rules apply to every agent: Arumi Studios as the only author, no AI attribution, PRs never merged by agents.

## Claude in Chrome (browser) sessions

Some sources are reachable only from the user's own browser. A browser session follows a brief from the repository
(Fondasi: [data-requests.md](data-requests.md)), collects raw files with a `SOURCE.txt`, and hands them to a
cloud session; it never commits personal data and never signs in with the user's accounts unless the user asks.
