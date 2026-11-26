# Progress

Shared working memory across sessions and Claude accounts. Read first, update last (`fondasi-session`).
No secrets, emails or personal data.

## Current phase

**Foundation, data round.** Rules and standards are in place (F-001…F-025, merged through PR #4): server flow and
app contract, settings/storage/Turnstile, conventions (Indonesian for everything users see), web baseline, UI and
feedback, Codex visual assets, agent workflow, assets, AI assistant, printing/QR/visitors, guides, decoration without
limits, detailed student data, calendar layers, adoption procedure for any repo. Data sets ready: `wilayah`,
`sekolah` (SD/MI only), `tahun-ajaran`, `skema-siswa`, `kaldik-jateng` (2026/2027). The round now fills the planned
data sets.

Environment: Claude cloud environment **Fondasi** (only `arumiforge/fondasi`, setup `.claude/cloud/setup.sh`, no
PHP/MySQL). The user prefers unrestricted network for it (may switch it to Full in Settings); until then the hosts in
`docs/cloud-environment.md` are allowed. Sources blocked from the cloud go through Claude in Chrome briefs
(`docs/data-requests.md`); the user runs those and uploads the zip.

**Standing permission (user, 2026-11-25):** sessions in this repository may merge their own PRs into `main` once CI is
green and there is no conflict, then report (F-026). The GitHub merge API sometimes answers 500/502 for this repository:
retry once later; if it still fails, ask the user to merge in the GitHub UI.

## Active work

| Branch | Session label | Task | Status |
| --- | --- | --- | --- |
| (none) | — | R-01 finished (PRs #9, #10 merged); next session picks from Next steps | — |

## Next steps (in this order, one PR per data set; interview the user when something is ambiguous)

1. **R-01 is done** (`sekolah` 2026-11-26, all levels). To refresh it later: `fetch --groups=dikdas,dikmen,paud,dikmas
   <raw> <regency codes>` in up to twenty workers (F-029; split the 514 regencies by size, ≈ 500 pages/min, ≈ 1 h for
   all 31,000 pages), then `build --groups=dikdas,dikmen,paud,dikmas`. Cloud containers are suspended a few minutes
   after the session goes idle: keep a Monitor on the worker logs and relaunch after a restart.
2. **R-06** waits for the user's zip from brief R-06 (Kanwil site times out from the cloud).
3. **R-10b** waits for the user's zip (PASI U14/U16, O2SN, POPDA/POPNAS); then extend `atletik-*`. **R-11** records
   need the user's list of championships.
4. When the user uploads R-12 or R-02/R-07/R-08/R-09 zips: verify SHA-256, keep raw files in `sources/<set>/`,
   build the set.
5. `wilayah` upstream (cahyadsn) now follows Kepmendagri 300.2.2-2430/2025: refresh `wilayah` and `kodepos` together.
6. Later (in app repositories, not here): SPMB `check-app` adapter, SPMB income list migration (F-024), SPMB data
   via `fondasi-sync`.

## Blockers / waiting on

- Hosts blocked from cloud sessions: `jateng.kemenag.go.id` (times out since 2026-11-25; R-06 brief), `kemenag.go.id` (refused), `emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`, `kurikulum.kemendikdasmen.go.id`
  (and `disdikbud.jatengprov.go.id`, replaced by `pdk.jatengprov.go.id`) → browser briefs.
- The Claude GitHub App may need access to the renamed repository for PR notifications (GitHub → Apps → Claude).

## Session log (newest first, keep the last 10)

- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — PR #9 merged (Dikdas+Dikmen); F-029 (parallel crawl, 20 workers on referensi.data); PAUD+PKBM/SKB crawled in 25 min, `sekolah` 539,580 units (98.0 % with village code), PR #10 merged. Next: R-06/R-10b zips from the user, `wilayah` refresh.
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — PR #8 was already merged; R-01 crawler extended (PAUD, Dikmas, page checks), F-028 (forms kept, PKBM/SKB only, no schools abroad), full Dikdas+Dikmen crawl (15,633 pages), `sekolah` 2026-11-26 built (283,421 schools, 97.8 % with village code), PR 1 opened. Next: PAUD+PKBM/SKB (part 2).
- 2026-11-26 · session data-round · `data/atletik` — PRs #5, #6 (libur-nasional, kaldik-jateng check), #7 (kodepos) merged; R-06 and R-10b briefs; R-10 World Athletics sets (F-027); R-01 crawler written, crawl not finished. Next: R-01 crawl.
- 2026-11-25 · session data-round · `data/libur-nasional` — PR #5 merged; R-01 interview (all provinces, replace SD/MI, madrasah from Kemendikdasmen with R-02 for NSM, add PAUD and PKBM/kesetaraan, sequential crawl in two PRs); R-04 built; R-06 moved to a browser brief (Kanwil site times out). Next: R-03 while the R-01 crawl runs.
- 2026-11-25 · session data-round prep · `pw/peaceful-tesla-bjooc9` — PR #4 merged (skema-siswa corrections F-024, kaldik-jateng, calendar layers F-025); environment Fondasi created; handoff for the data round. Next: R-01.
- 2026-11-25 · session server-flow · `pw/peaceful-tesla-bjooc9` — repository created and filled: F-001…F-023 (PRs #1–#3), interview rounds with the user, first data sets. Next: data round.
