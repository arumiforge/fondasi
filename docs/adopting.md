# Adopting Fondasi in a repository (F-016)

Fondasi gives every repository the same **base**; the details of each app are decided later by the user and Claude
in that repository. This page is the procedure a Claude session follows in another repository (new or existing),
with the `fondasi-adopt` skill.

## How the user starts it

In a Claude Code session of the app repository, paste:

```
Lampirkan repo arumiforge/fondasi (add_repo), baca CLAUDE.md dan docs/adopting.md di sana, lalu jalankan
skill fondasi-adopt untuk repo ini: telaah dan audit repo ini terhadap Fondasi, laporkan hasilnya, tanya saya
untuk keputusan yang perlu, dan siapkan dasarnya. Jangan ubah kode aplikasi sebelum saya setuju.
```

Shorter, once the app's `CLAUDE.md` already has the Fondasi pointer: "Audit repo ini terhadap Fondasi."

Cloud environment: add `arumiforge/fondasi` as a second repository of the app's environment
([cloud-environment.md](cloud-environment.md)), or let the session attach it with `add_repo`. Once attached, Fondasi's
skills (`fondasi-*`, `bahasa-indonesia-plain`) are available in that session.

## What Claude does

1. **Read** Fondasi (`CLAUDE.md`, decisions, the docs the app touches) and the app repository (README, stack files,
   routes, views, migrations, CI, deploy files, existing `CLAUDE.md`/`AGENTS.md`/docs). No changes yet.
2. **Audit** the app against each area below and write the report (format below) as `docs/fondasi-audit.md` in
   the app repository, on a branch.
3. **Ask** the user only what the repository cannot answer: purpose and users, clients (public institution or not —
   storage rule F-006), chat language, which gaps to fix first, any rule that should be an exception. Use a short
   interview (a few questions at a time); record answers as `D-…` decisions in the app.
4. **Set up the base** (small PRs, never merged without the user):
   - `CLAUDE.md` from `templates/repo/CLAUDE.md` (keep what the repo already had, add the Fondasi block, language,
     commit rules; leave app-specific sections as placeholders to fill with the user);
   - `AGENTS.md`, `.githooks/commit-msg`, `.github/workflows/commit-policy.yml` from `templates/repo/`;
   - `.claude/skills/<app>-session/` from `templates/repo/.claude/skills/app-session/` (F-017), adapted;
   - `docs/progress.md` and `docs/decisions.md` (D-001 "Adopt Fondasi at <commit>") from `templates/repo/docs/`;
   - `ai/` from `templates/ai/` only when the app needs visual assets;
   - on the server, a `PORTS` line with the hostname and, when useful, a `check-app` adapter.
5. **Plan** the fixes: the audit's gaps as ordered next steps in `docs/progress.md`; the user chooses what comes first.

Never rewrite working code just to match a rule in one go; never copy SPMB's own choices (modules, roles, school
identity) into another app — only Fondasi's rules.

## Audit areas

| Area | Fondasi source | Typical checks |
| --- | --- | --- |
| Repository conventions | `conventions.md` | language split, Indonesian URLs, commit author and attribution, hooks/CI, licence and notices |
| Everything users see is Indonesian | `conventions.md` (F-012) | UI, emails, PDFs, file names, export headers, status labels |
| Web baseline | `web-baseline.md` | security headers, cookies, CSRF, passwords, rate limits, 2FA, permissions/ownership, uploads, personal data, audit log, identity fields, performance, `/healthz`, staging closed, tests, public pages |
| UI | `ui.md` | the "Never" list, states, forms, responsive, accessibility, formats, white label |
| Feedback | `feedback.md` | tier of every message, placement, focus, no-JS fallback |
| Settings and storage | `settings.md`, `storage.md` | env names, env wins over panel, where files and personal data live |
| Server | `app-contract.md`, `server-playbook.md` | folder, port on 127.0.0.1, compose rules, backups, deploy flow, tunnel route |
| Shared data | `data.md` | regions/schools/calendars kept by hand that should come from `fondasi-sync` |
| Agent workflow | `agent-workflow.md` | `CLAUDE.md`, `AGENTS.md`, `progress.md`, `decisions.md`, an `<app>-session` skill |
| Assets | `assets.md` | minified served copies, originals kept, versioned URLs, self-hosted libraries |
| AI assistant (if any) | `ai-assistant.md` | answer order, provider rotation and failover, limits, masking |
| Guides | `guides.md` | per-role guide pages, article anatomy, updated with features |
| Detailed student data (internal school apps) | `school-data.md` | agreement, permissions per field group, sensitive groups, retention |
| School administration features (school apps) | `school-admin.md` | which catalog features the app builds (recorded as `D-…`), sensitivity of each, rules for biometrics, BK, reports, money, notifications |
| Decoration and loading | `ui.md`, `web-baseline.md` §6 | page usable before decoration, skeletons, Codex-made art |
| Printing, QR, visitors | `web-baseline.md` §11–12 | A4/F4, unique QR tokens, logo with level H, daily-salted visitor hash |
| Visual assets | `visual-assets.md` | `ai/` briefs, Codex workflow, style guide |

## Report format (`docs/fondasi-audit.md` in the app)

```markdown
# Fondasi audit — <app> (<date>, Fondasi <commit>)

Summary: <3–5 lines: overall state, biggest risks, suggested order>.

| Area | Rule | Status | Evidence | Fix | Effort |
| --- | --- | --- | --- | --- | --- |
| Web baseline | Security headers | missing | no CSP/HSTS in `nginx.conf` | add headers | S |
| Conventions | Indonesian URLs | partial | `/admin/users` | rename + 301 | M |
| … | … | ok / partial / missing / n/a (reason) | file:line | … | S/M/L |

Questions for the user: <numbered>.
Proposed first steps: <ordered list>.
```

Status `n/a` always carries a reason. Re-run the audit after big changes or a new Fondasi decision; the report keeps
its date and the Fondasi commit it was checked against.
