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
| `nty/eager-tesla-92hwl9` | session data-round 3 | R-15 `capaian-pembelajaran` converter (in progress, handed over) | handed over (session too long) |

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
   **R-15 `capaian-pembelajaran` — in progress, next task** (F-030, F-032). State:
   - `tools/converters/capaian-pembelajaran.py` (committed, not yet run into `data/`). Full build:
     `python3 -I tools/converters/capaian-pembelajaran.py sources/capaian-pembelajaran data` (≈ 2 min; needs
     pdftotext and pdfplumber, both present in the cloud image). It parses 046 Lampiran I (PAUD), II (40 subjects
     without religion), III (183 SMK sections), IV (11 Paket), V (43 SLB without religion) and SK 9941 (15 madrasah
     sections) into `data/capaian-pembelajaran/<file>.json.gz` + `index.json`, and stops on structure problems.
   - Last run stopped on ONE structure problem: 046 Lampiran V, XXXII.4 "Fase Fondasi Program Kebutuhan Khusus
     Pengembangan Diri dan Gerak … Hambatan Fisik/Tunadaksa" (PDF p. 1609–1612): no phase found (its D section
     probably lacks "Pada akhir Fase Fondasi"; look with `pdftotext -layout -f 1609 -l 1612`). Fix, rerun, then:
     manifest (version = newest source date of what is included: 046 is 2025-07-16, SK 9941 is 2025-11-28, so
     2025-11-28), `tools/data-check --write`, README row, CHANGELOG, PR.
   - Per subject the output has `source_notes`: element names that differ between the element table and the CP
     headings in the source (e.g. "Aljabar" vs "Aljabar dan Fungsi", German "Menyimak (Hören)" vs "Menyimak"); they
     are source facts, not parser errors. "-" in the source is stored as `text: null, no_cp: true`.
   - Spot-check a few outcomes per file against the PDF before publishing (text is extracted, not transcribed).
   - Then the religion PR (F-032): Kepka BKPDM 020/2026 is a scan; OCR (tesseract `ind`, 300 dpi,
     OMP_THREAD_LIMIT=1, 4 in parallel, ≈ 1 min for 79 pages; `apt-get install tesseract-ocr tesseract-ocr-ind`)
     is a draft only. SD phases A–C: use sinaubareng `docs/data/curriculum/cp-pendidikan-agama-sd-bkpdm-020-2026.json`
     (checked word by word); D–F and Lampiran II (special education) must be read from page images.
   Then **R-16 `kerangka-tka`**, then **R-17** coordinates for `sekolah` (crawl of NPSN pages, 20 workers, F-029).
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

- 2026-11-26 · session data-round 3 · `nty/eager-tesla-92hwl9` — R-15 started: generic CP parser for 046 (all appendices) and SK 9941 written and run (≈ 2,900 outcomes); F-032 (religion from 020 in a checked second step, full content). Handed over before the first data build (one SLB section left). Next: finish R-15.

- 2026-11-26 · session data-round 3 · `nty/eager-tesla-92hwl9` — PRs #16 (O2SN) and #17 (sinaubareng audit) merged; R-08 `mapel` built for all levels (54 tables, 144 totals checked, 7 errata, F-031; user: Bahasa Inggris SD/MI compulsory from 2027/2028 = Pasal 33). Next: R-15.

- 2026-11-26 · session data-round 3 · `nty/eager-tesla-92hwl9` — PR #15 found merged; R-10b O2SN part built (guides + the two scoring tables fetched from the guides' links, every row matches WA formulas; women's 60 m parameters derived). sinaubareng audited (user: mapel all levels, CP all subjects, TKA, coordinates later; repo to be made private by the user).
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — R-06 built from the uploaded Kanwil decree 1681/2026 (45 events, HK/HL/HE of all 12 months match); O2SN 2026 guides stored for R-10b. Next: merge the R-06 PR, then O2SN.
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — R-14 brief written; the user uploaded Kepmendagri 2430/2025: it changes islands only, `wilayah` already matches; decree kept in `sources/wilayah/`. Next: R-06/R-10b zips, R-11 list.
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — `wilayah`/`kodepos` refresh checked: upstream data unchanged (README ahead of `wilayah.sql`), nothing to rebuild. Next: R-06/R-10b zips, official 2430/2025 attachment if wanted.
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — PR #9 merged (Dikdas+Dikmen); F-029 (parallel crawl, 20 workers on referensi.data); PAUD+PKBM/SKB crawled in 25 min, `sekolah` 539,580 units (98.0 % with village code), PR #10 merged. Next: R-06/R-10b zips from the user, `wilayah` refresh.
- 2026-11-26 · session data-round 2 · `nty/amazing-knuth-svvihr` — PR #8 was already merged; R-01 crawler extended (PAUD, Dikmas, page checks), F-028 (forms kept, PKBM/SKB only, no schools abroad), full Dikdas+Dikmen crawl (15,633 pages), `sekolah` 2026-11-26 built (283,421 schools, 97.8 % with village code), PR 1 opened. Next: PAUD+PKBM/SKB (part 2).
- 2026-11-26 · session data-round · `data/atletik` — PRs #5, #6 (libur-nasional, kaldik-jateng check), #7 (kodepos) merged; R-06 and R-10b briefs; R-10 World Athletics sets (F-027); R-01 crawler written, crawl not finished. Next: R-01 crawl.
- 2026-11-25 · session data-round · `data/libur-nasional` — PR #5 merged; R-01 interview (all provinces, replace SD/MI, madrasah from Kemendikdasmen with R-02 for NSM, add PAUD and PKBM/kesetaraan, sequential crawl in two PRs); R-04 built; R-06 moved to a browser brief (Kanwil site times out). Next: R-03 while the R-01 crawl runs.
