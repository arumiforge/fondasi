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
| `nty/sekolah-koordinat` | session data-round 6 | R-17 latitude/longitude for every unit of `sekolah` (crawl of `/satpen/detail/<npsn>`, 160 threads on one queue, F-029) | crawl running |

## Next steps (in this order, one PR per data set; interview the user when something is ambiguous)

1. **R-01 is done** (`sekolah` 2026-11-26, all levels). To refresh it later: `fetch --groups=dikdas,dikmen,paud,dikmas
   <raw> <regency codes>` in up to twenty workers (F-029; split the 514 regencies by size, ≈ 500 pages/min, ≈ 1 h for
   all 31,000 pages), then `build --groups=dikdas,dikmen,paud,dikmas`. Cloud containers are suspended a few minutes
   after the session goes idle: keep a Monitor on the worker logs and relaunch after a restart.
2. **R-06 done** (`kaldik-madrasah-jateng` 2026-06-29, PR #15 merged). Still missing: the national guideline Keputusan Dirjen Pendis 4860/2026 (optional; the Kanwil decree
   follows it). The 4 SKB 2027 cuti bersama days not in the decree are listed in `skb_days_not_in_this_calendar`.
3. **R-10b, O2SN part done** (atletik sets 2026-11-26): eligibility groups, events, implements, Kids' Athletics
   courses, qualifying marks and scoring (all 17,595 rows of the linked tables checked). Still missing: PASI U14/U16
   and POPDA/POPNAS (brief R-10b items 1 and 3); O2SN 2027 when Puspresnas publishes it. **R-11** records need the
   user's list of championships.
4. **R-08 done** (`mapel` 2025-09-22, all levels incl. madrasah; F-031 errata). Open in it: KMA Tabel 18 (MILB V)
   totals count 36 kokurikuler JP more than its rows (`unresolved`); check again when Kemenag publishes a corrected KMA.
   **R-15 `capaian-pembelajaran`** (2026-06-11; F-030, F-032): 046 + 9941 (PR #20) and the religion CP of 020
   Lampiran I (`agama.json.gz`, 192 outcomes) are in. Rebuild: `python3 -I tools/converters/capaian-pembelajaran.py
   sources/capaian-pembelajaran data` (≈ 2 min) then `python3 -I tools/converters/capaian-pembelajaran-agama.py
   sources/capaian-pembelajaran data` (seconds; rewrites index.json). **R-15 is complete**: 020 Lampiran II (special-education religion CP, `pendidikan-khusus-agama.json.gz`, 192
   outcomes) is in too; transcription `transkripsi-020/2.1-*.txt` … `2.6-*.txt`. New printing errors go to `ERRATA` in
   `capaian-pembelajaran-agama.py`.
   **R-16 done** (`kerangka-tka` 2026-03-06): framework SD/MI and SMP/MTs from 047, administration from 56/2026;
   rebuild `python3 -I tools/converters/kerangka-tka.py sources/kerangka-tka data`. Add the SMA/SMK framework when
   BSKAP publishes one (F-033). Sample questions and the 2026 category limits (secondary) are in; replace the limits
   when an official document states them. Next: **R-17** coordinates for `sekolah` (crawl of NPSN pages, 20 workers, F-029).
5. When the user uploads R-12 or R-02/R-07/R-09 zips: verify SHA-256, keep raw files in `sources/<set>/`,
   build the set.
6. `wilayah` / `kodepos`: **current** (R-14 done 2026-11-26). Kepmendagri 300.2.2-2430/2025 changes only island
   data (four islands move to Aceh Singkil); `data/wilayah` 2026-02-13 matches its region totals exactly, and
   `kodepos` is unaffected. Check again when Kemendagri publishes a new decree on region codes (cahyadsn usually
   follows within months; compare the header of `db/wilayah.sql`).
7. Later (in app repositories, not here): SPMB `check-app` adapter, SPMB income list migration (F-024), SPMB data
   via `fondasi-sync`.

## Blockers / waiting on

- Hosts blocked from cloud sessions: `jateng.kemenag.go.id` (times out since 2026-11-25; R-06 brief), `kemenag.go.id` (refused), `jdih.kemendagri.go.id` (no answer, 2026-11-26), `emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`, `kurikulum.kemendikdasmen.go.id`
  (and `disdikbud.jatengprov.go.id`, replaced by `pdk.jatengprov.go.id`) → browser briefs.
- The Claude GitHub App may need access to the renamed repository for PR notifications (GitHub → Apps → Claude).

## Session log (newest first, keep the last 10)

- 2026-11-27 · session data-round 5 · `nty/kerangka-tka-atribusi` — PR #24 merged. F-034 (third-party works for education with credit); attribution added to every `kerangka-tka` stimulus. Next: R-17.
- 2026-11-27 · session data-round 5 · `nty/kerangka-tka-contoh-soal` — PR #23 merged. `kerangka-tka`: 24 sample questions of 047 with 13 figures (keys recomputed, 4 errata) and the 2026 category limits marked secondary (F-033). Next: R-17.
- 2026-11-26 · session data-round 5 · `nty/kerangka-tka` — PR #22 merged (religion CP Lampiran II, R-15 complete). R-16 `kerangka-tka` built from 047 and 56/2026 (4 frameworks, every text unit and table cell checked against the PDFs, schedule read on the page images, 3 errata). Next: R-17.
- 2026-11-26 · session data-round 5 · `nty/cp-agama-pendidikan-khusus` — 020 Lampiran II transcribed from page images (2.1–2.6, 192 outcomes, every pinyin/diacritic line on zoomed crops, OCR diff clean), `pendidikan-khusus-agama.json.gz` built, `capaian-pembelajaran` complete (305 subjects, 2,816 outcomes). Next: R-16 `kerangka-tka`.
- 2026-11-26 · session data-round 4 · `nty/serene-hamilton-q7whfv` — PR #20 merged (046 + 9941). Religion CP of 020 Lampiran I transcribed from page images (6 religions, 192 outcomes; SD A–C identical to sinaubareng), `agama.json.gz` built, version 2026-06-11. Next: 020 Lampiran II.
- 2026-11-26 · session data-round 4 · `nty/serene-hamilton-q7whfv` — R-15 finished without religion: last SLB section fixed, converter hardened (signature block with NIP cut, PAUD scope tables, SK 9941 merged-cell tables, ligatures, title case, F-031 errata), every outcome checked verbatim against the PDF text; `capaian-pembelajaran` 2025-11-28 built. Next: religion CP (020/2026).
- 2026-11-26 · session data-round 3 · `nty/eager-tesla-92hwl9` — R-15 started: generic CP parser for 046 (all appendices) and SK 9941 written and run (≈ 2,900 outcomes); F-032 (religion from 020 in a checked second step, full content). Handed over before the first data build (one SLB section left). Next: finish R-15.
- 2026-11-26 · session data-round 3 · `nty/eager-tesla-92hwl9` — PRs #16 (O2SN) and #17 (sinaubareng audit) merged; R-08 `mapel` built for all levels (54 tables, 144 totals checked, 7 errata, F-031; user: Bahasa Inggris SD/MI compulsory from 2027/2028 = Pasal 33). Next: R-15.
- 2026-11-26 · session data-round 3 · `nty/eager-tesla-92hwl9` — PR #15 found merged; R-10b O2SN part built (guides + the two scoring tables fetched from the guides' links, every row matches WA formulas; women's 60 m parameters derived). sinaubareng audited (user: mapel all levels, CP all subjects, TKA, coordinates later; repo to be made private by the user).
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — R-06 built from the uploaded Kanwil decree 1681/2026 (45 events, HK/HL/HE of all 12 months match); O2SN 2026 guides stored for R-10b. Next: merge the R-06 PR, then O2SN.
