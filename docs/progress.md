# Progress

Shared working memory across sessions and Claude accounts. Read first, update last (`fondasi-session`).
No secrets, emails or personal data.

## Current phase

**Foundation round 1** (F-001…F-011): server rules and scripts moved from SPMB (D-112) and made app-neutral,
app contract, several-servers rules, settings/storage/Turnstile standards, data framework (`fondasi-sync`,
`data-check`), first sets (`wilayah`, `sekolah` SD/MI, `tahun-ajaran`), shared skills, cloud environment, data
request briefs, conventions (Indonesian URLs, no AI attribution), UI rules against generic AI design, Codex
visual-asset workflow and templates.

## Active work

| Branch | Session label | Task | Status |
| --- | --- | --- | --- |
| `pw/peaceful-tesla-bjooc9` | session server-flow | Foundation round 1 | PR open |

## Next steps

1. User: rename the repository to `fondasi` (GitHub → Settings → Repository name; old URLs redirect). Then in
   SPMB: paste the pointer block (`docs/app-pointer.md`) into `CLAUDE.md`, and later switch SPMB's
   `deploy/server/check.sh`/`setup.sh` to Fondasi's copies (or keep both in step until then).
2. On `spmb-prod`: deploy key for Fondasi, clone to `/opt/apps/_fondasi`, run its `check.sh`; add hostnames as
   the third column of `/opt/apps/PORTS` and record `milklife-staging`'s port; fill the `docs/servers.md` row.
3. Data, cloud session (hosts reachable): R-01 schools of every level from Dapodik/referensi (start with
   Jawa Tengah; new schema with region codes linking to `wilayah`), R-03 postal codes, R-04 SKB holidays,
   R-06 madrasah calendar Jateng, R-10 athletics rules from World Athletics.
4. Data, browser sessions (Claude in Chrome): R-02 EMIS madrasah, R-05 Kaldik Jateng, R-07 Dapodik code
   tables, R-08 curriculum subjects, R-09 PDDikti; R-11 needs the user's list of championships.
5. Every app repo: copy `templates/repo/` (AGENTS.md, hook, commit policy) and, for visuals, `templates/ai/`;
   SPMB already has its own `ai/` (the model for the templates).
6. SPMB later: import `wilayah`/`sekolah` through `fondasi-sync` instead of its own copies; Turnstile and S3
   storage following `docs/settings.md` / `docs/storage.md` (not started).

## Blockers / waiting on

- Repository rename to `fondasi` (user).
- Hosts blocked from cloud sessions: `emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`,
  `disdikbud.jatengprov.go.id`, `kurikulum.kemendikdasmen.go.id` → browser briefs.
- Not yet rehearsed on a VM: `setup.sh` on a server already running containers (logic unit-tested in SPMB D-112).

## Session log (newest first, keep the last 10)

- 2026-11-25 · session server-flow · `pw/peaceful-tesla-bjooc9` — repository created; interview (name, pinned data copies, all school levels, calendars, athletics, storage, env vs panel, more shared data, several VPS); round 1 built. Next: rename, server checkout, data R-01/R-03/R-04.
