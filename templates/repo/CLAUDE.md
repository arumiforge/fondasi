# <App name> — Agent Guide

<One or two sentences: what the app does, for whom, first client.> Built by **Arumi Studios**.

Start every session with the `<app>-session` skill (Fondasi `docs/agent-workflow.md`): read `docs/progress.md`
(state, active work, next steps) and update it before you finish.
Decisions: `docs/decisions.md` (`D-…`). Never implement against a recorded decision — ask, or record a new one.

## Fondasi (shared rules, data and skills)

This app follows `arumiforge/fondasi`. When the work touches the server or deploys, storage, settings, shared
reference data, security or personal data, Indonesian user-facing text, UI design, user feedback or visual assets:
attach it (`add_repo arumiforge/fondasi`), read its `CLAUDE.md` and follow its skills. Its decisions (`F-…`) apply
here unless this repository records an exception in `docs/decisions.md`. Shared data and skills are copied with its
`tools/fondasi-sync` (`fondasi.lock`), never edited by hand.

## Language (Fondasi F-009, F-012)

Docs, code, comments, commits and PRs in English. Everything users see, download or receive — UI, URLs, emails,
PDFs, exports — in plain Indonesian. Chat replies: <English | Indonesian — the user's choice>.

## Commits (strict)

Author and committer `Arumi Studios <arumiforge@gmail.com>`; no AI attribution anywhere; Conventional Commits;
`git config core.hooksPath .githooks`. Agents open PRs and never merge unless the user asks.

## Stack

<Language, framework, database, front end, how it runs locally and on the server — filled in with the user.>

## Commands

```bash
<install / run / test / lint / build>
```

## App-specific rules

<Added with the user as decisions are made: modules, roles and permissions, identity of the visuals, clients.>
