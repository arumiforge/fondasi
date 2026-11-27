# Fondasi — Agent Guide

Shared foundation for every **Arumi Studios** application (education, athletics, school admission
(SPMB) and related public services). One place for what would otherwise be re-decided in every repo:

| Area | Folder | Read |
| --- | --- | --- |
| Server: preparing a VPS, checking it, the contract every app on it follows | `server/` | `docs/server-playbook.md`, `docs/app-contract.md` |
| Standards: settings (env vs panel), file storage (local, S3/R2), Turnstile, secrets | — | `docs/settings.md`, `docs/storage.md` |
| Public reference data: regions, schools, calendars, Dapodik references, athletics… | `data/` | `docs/data.md`, `data/README.md` |
| Conventions for every repo: language, Indonesian URLs, commits without AI attribution | `templates/repo/` | `docs/conventions.md` |
| Web app baseline: security, uploads, personal data, audit log, Indonesian identity fields, performance, monitoring, staging, tests, public pages | — | `docs/web-baseline.md` |
| UI/UX rules against generic AI-made design; feedback (toast, undo, form errors, dialogs, banners) | — | `docs/ui.md`, `docs/feedback.md` |
| Visual assets made by Codex from briefs in each app's `ai/` | `templates/ai/` | `docs/visual-assets.md` |
| How agents work in every repo: progress, decisions, tasks, context, handoff, parallel sessions | `templates/repo/.claude/skills/app-session/` | `docs/agent-workflow.md` |
| Front-end assets: minified served copies, originals kept, versioned URLs | — | `docs/assets.md` |
| AI help assistant: OpenAI-compatible providers, round robin, Gemini, limits | — | `docs/ai-assistant.md` |
| In-app guide pages (GitHub Docs style, richly decorated by Codex) | — | `docs/guides.md` |
| Detailed student data in internal school apps; student data schema | `data/skema-siswa/` | `docs/school-data.md` |
| Adopting Fondasi in another repository: audit, interview, base setup | `templates/repo/` | `docs/adopting.md` |
| Agent skills shared by every repo (`fondasi-adopt`, `fondasi-session`, `-server`, `-data`, `-web`, `-ui`, `-feedback`, `-visual`, `-ai`, `-guides`, `bahasa-indonesia-plain`) | `.claude/skills/` | below |

Start every session with the `fondasi-session` skill and read `docs/progress.md`; update it before
you finish. Decisions live in `docs/decisions.md` (IDs `F-001`…, separate from each app's own `D-…`).
Never implement against an assumption that contradicts a recorded decision — ask, or record a new one.

## How app repositories use Fondasi

Apps never import code from here at runtime. They follow its rules and copy what they need:

- **Rules**: each app's `CLAUDE.md` carries the pointer block from `docs/app-pointer.md`. A Claude
  session in that app attaches `arumiforge/fondasi` (`add_repo`) when it touches the server, storage,
  settings, shared data or Indonesian copy, and follows the skills here.
- **Data**: `tools/fondasi-sync` copies one data set at a pinned version into the app
  (`<app>/data/fondasi/<set>/` + `fondasi.lock`), verified by `SHA256SUMS`. Updating = a deliberate sync
  and commit in the app (F-003).
- **Server**: the VPS has one checkout at `/opt/apps/_fondasi`; `setup.sh` and `check.sh` run from there.

## Language rules (strict)

| Surface | Language |
| --- | --- |
| Replies to the user in chat | Indonesian when the user asks for it (current preference), otherwise English |
| `docs/`, `*.md`, code comments, commit messages, PRs | English |
| Data labels that apps show to users (`label` fields) | Official Indonesian names as the source writes them |
| UI text written from these rules in apps | Friendly, plain Indonesian — `bahasa-indonesia-plain` skill |

## Commit and contributor rules (strict)

- Author and committer: `Arumi Studios <arumiforge@gmail.com>` (`git config user.name` / `user.email`).
- **No AI attribution anywhere**: no `Co-Authored-By`, no `Claude-Session`, no "Generated with" lines in
  commits, PR bodies or comments. Enforced by `.githooks/commit-msg` (`git config core.hooksPath .githooks`)
  and `.github/workflows/commit-policy.yml`.
- Conventional Commits: `feat(data): …`, `feat(server): …`, `docs: …`, `fix: …`, `chore: …`.
- PR tools that append an AI footer automatically: remove it from the PR body right after creating the PR.
- Codex (and any other agent) follows `AGENTS.md`.

## Data rules (strict)

- Only **public data without personal data** lives here. Never names of students, parents, athletes'
  private details, NIK, NISN, phone numbers.
- Every data set has `manifest.json` (source, licence, version, counts), `SHA256SUMS`, and a converter or
  documented procedure that rebuilds it from the source. Sources are untrusted input: parse, never execute.
- A version is a date (`YYYY-MM-DD`, the source's date). Changing data = new version + changelog line.
- Licences: record each source's licence in `THIRD_PARTY_NOTICES.md`; MIT/BSD/Apache/ISC/CC-BY/public
  government data are fine; third-party works used for education are fine when their owners are credited
  (`attribution`, F-034); ask before anything else.

## Licence

Proprietary, © Arumi Studios (`LICENSE`). The repository stays **private**.
