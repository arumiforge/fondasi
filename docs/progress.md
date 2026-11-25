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
| `data/sekolah-semua-jenjang` | session data-round | R-01: Dikdas + Dikmen of every province (crawl running, ~8 h); PAUD + Dikmas in a second PR | crawling |
| `data/libur-nasional` | session data-round | R-04 `libur-nasional` 2026, 2027; `kaldik-jateng` checked against it; R-06 brief (browser) | PR #6 merged |
| `data/kodepos` | session data-round | R-03 `kodepos` | PR #7 |

## Next steps (in this order, one PR per data set; interview the user when something is ambiguous)

1. **R-01 `sekolah` all levels**: SMP, MTs (where Dapodik lists them), SMA, MA, SMK, SLB from `dapo.kemendikdasmen.go.id` /
   `referensi.data.kemendikdasmen.go.id`, start with Jawa Tengah, then all provinces; new schema with the village/district
   region codes of `wilayah`, NPSN, name, level, public/private, address; keep the SD/MI part; converter in
   `tools/converters/`, polite rate (≥ 1 s between requests), version = source date. Madrasah gaps → R-02 (browser).
2. **R-04 `libur-nasional`**: SKB 3 Menteri on national holidays and cuti bersama 2026 and 2027 from `kemenkopmk.go.id`
   (raw PDFs to `sources/libur-nasional/`); then reconcile the `estimate` events and the notes in `kaldik-jateng`.
   **R-06 `kaldik-madrasah-jateng`**: Kanwil Kemenag Jawa Tengah madrasah calendar 2026/2027 (`jateng.kemenag.go.id`).
3. **R-03 `kodepos`**: postal code per village code (cahyadsn wilayah postal list; check its licence first, ask the user
   if it is not MIT/BSD/Apache/ISC/CC-BY/public government data).
4. **R-10 athletics**: `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil` from World Athletics rules (and PASI /
   O2SN technical handbooks via a browser brief where blocked). Ask the user which championships and age groups matter
   before R-11 records.
5. When the user uploads **R-12** (national education calendar + SKB) or R-02/R-07/R-08/R-09 zips: verify SHA-256,
   keep raw files in `sources/<set>/`, build the set.
6. Later (in app repositories, not here): SPMB `check-app` adapter, SPMB income list migration (F-024), SPMB data via
   `fondasi-sync`.

## Blockers / waiting on

- Hosts blocked from cloud sessions: `jateng.kemenag.go.id` (times out since 2026-11-25; R-06 brief), `kemenag.go.id` (refused), `emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`, `kurikulum.kemendikdasmen.go.id`
  (and `disdikbud.jatengprov.go.id`, replaced by `pdk.jatengprov.go.id`) → browser briefs.
- The Claude GitHub App may need access to the renamed repository for PR notifications (GitHub → Apps → Claude).

## Session log (newest first, keep the last 10)

- 2026-11-25 · session data-round · `data/libur-nasional` — PR #5 merged; R-01 interview (all provinces, replace SD/MI, madrasah from Kemendikdasmen with R-02 for NSM, add PAUD and PKBM/kesetaraan, sequential crawl in two PRs); R-04 built; R-06 moved to a browser brief (Kanwil site times out). Next: R-03 while the R-01 crawl runs.
- 2026-11-25 · session data-round prep · `pw/peaceful-tesla-bjooc9` — PR #4 merged (skema-siswa corrections F-024, kaldik-jateng, calendar layers F-025); environment Fondasi created; handoff for the data round. Next: R-01.
- 2026-11-25 · session server-flow · `pw/peaceful-tesla-bjooc9` — repository created and filled: F-001…F-023 (PRs #1–#3), interview rounds with the user, first data sets. Next: data round.
