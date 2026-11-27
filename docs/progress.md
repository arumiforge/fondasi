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
| `nty/eloquent-davinci-myz72i` | session data-round 6 | R-18 `batas-wilayah`: PR #26 merged (Kudus); PR #28 `presisi` + cross-regency topology | PR #28 merged |
| `nty/sekolah-koordinat` | session data-round 6 | R-17 latitude/longitude for every unit of `sekolah` (F-036) | PR #27 merged |
| `nty/magical-ramanujan-54d9nu` | session data-round 7 (account A) | R-18 `batas-wilayah` for all of Jawa Tengah (Next steps 7); only `tools/converters/batas-wilayah.py`, `data/batas-wilayah/`, `sources/batas-wilayah/` | PR #30 merged; scope stays at Jawa Tengah |
| `nty/magical-ramanujan-54d9nu` | session data-round 7 (account A) | R-10b delivery (POPDA Jateng 2026 juknis, POPNAS age rule) into `atletik-*`; R-06/R-14 search records | PRs #34, #35 merged |
| `pw/practical-thompson-r2to0p` | session data-round 8 | R-11 `atletik-rekor` (PASI national records, World Athletics lists, F-037); only `tools/converters/atletik-rekor*`, `data/atletik-rekor/`, `sources/atletik-rekor/` | PR open |
| `pw/exciting-goldberg-mqpkx5` | akun-2 | R-18 support: `tools/checks/batas-wilayah.py` (coverage, areas, cross-regency arcs, `--big`, `--render`), docs/data.md "Using boundaries in apps", `fondasi-data` line. Does not touch the converter or `data/batas-wilayah/` | PR #29 merged |

## Next steps (in this order, one PR per data set; interview the user when something is ambiguous)

1. **R-01 is done** (`sekolah` 2026-11-26, all levels). To refresh it later: `fetch --groups=dikdas,dikmen,paud,dikmas
   <raw> <regency codes>` in up to twenty workers (F-029; split the 514 regencies by size, ≈ 500 pages/min, ≈ 1 h for
   all 31,000 pages), then `build --groups=dikdas,dikmen,paud,dikmas`. Cloud containers are suspended a few minutes
   after the session goes idle: keep a Monitor on the worker logs and relaunch after a restart.
2. **R-06 done** (`kaldik-madrasah-jateng` 2026-06-29, PR #15 merged). Still missing: the national guideline Keputusan Dirjen Pendis 4860/2026 (optional; the Kanwil decree
   follows it). The 4 SKB 2027 cuti bersama days not in the decree are listed in `skb_days_not_in_this_calendar`.
3. **R-10b done as far as sources allow** (atletik sets 2026-11-27): O2SN 2026 (all 17,595 table rows checked) and
   POPDA Jawa Tengah 2026 (Dispora juknis, page images; SMA putri shot printed "24 kg" kept as printed by the user's
   decision, with an unresolved erratum); POPNAS age rule as secondary. Still missing, no official copy reachable on
   2026-11-27: PASI U14/U16 rules (pasi.or.id does not resolve) and the POPNAS XVII athletics handbook; O2SN 2027 when
   Puspresnas publishes it (now at pusatprestasinasional.kemendikdasmen.go.id). PASI's site **www.pbpasi.org** was searched on 2026-11-28 (WordPress search and media
   API): no U14/U16 rule and no Kejurnas handbook; the Kejurnas 2024/2025 programmes from its result books are in
   `atletik-nomor` (`PASI_KEJURNAS_2024/2025`). U14/U16 rules now need the user or a Pengprov PASI document. **R-11 done** (`atletik-rekor`
   2026-11-27, F-037): PASI national records senior/U20/U18 and World Athletics world, world U20, world U18 best and
   Asian records. Refresh: `node tools/converters/atletik-rekor-fetch.mjs sources/atletik-rekor/wa` (needs
   Playwright: `NODE_PATH=/opt/node-tools/node_modules` in the cloud), curl the seven PASI pages listed in
   `sources/atletik-rekor/pasi/SOURCE.txt` into the same folder, bump `VERSION` in `tools/converters/atletik-rekor.py`,
   run it with `sources/atletik-rekor data`, then `tools/data-check --write`. Championship records (O2SN, POPDA,
   POPNAS, the user's championships) wait for a published list (user: "gunakan seadanya dulu").
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
   when an official document states them. **R-17 done** (`sekolah` 2026-11-27, F-036): coordinates of every unit from `/satpen/detail/<npsn>`. To refresh:
   `python3 -I tools/converters/sekolah.py coords data/sekolah <raw outside the repo> sources/sekolah/koordinat
   --threads=160` (≈ 7 h for 540,000 pages; resumable; delete the TSVs first for a new crawl), then `coords-merge
   data/sekolah sources/sekolah/koordinat sources/sekolah/batas-wilayah <date>` and `tools/data-check --write`.
   A list refresh (`build`) drops the coordinate fields: run `coords-merge` after it.
5. **R-09** waits for PDDikti (user, 2026-11-28: BIMA's e-catalog is partial, see data-requests). **R-07**: the
   uploaded Panduan Aplikasi Dapodik versi 2027 is a user manual without code tables; the user will send an export
   from the Dapodik application. Keep only reference tables from it, never student or staff rows.
   When the user uploads R-12 or R-02/R-07/R-09 zips: verify SHA-256, keep raw files in `sources/<set>/`,
   build the set.
6. `wilayah` / `kodepos`: **current** (R-14 done 2026-11-26). Kepmendagri 300.2.2-2430/2025 changes only island
   data (four islands move to Aceh Singkil); `data/wilayah` 2026-02-13 matches its region totals exactly, and
   `kodepos` is unaffected. Check again when Kemendagri publishes a new decree on region codes (cahyadsn usually
   follows within months; compare the header of `db/wilayah.sql`).
7. **R-18 `batas-wilayah`** (F-035): **all of Jawa Tengah done** (35 regencies, 8,563 villages, 576 districts; Kudus
   first in PR #26). **Scope stops at Jawa Tengah for now (user, 2026-11-27: "cukup jawa tengah dulu")**: no other
   province until the user asks. To rebuild or extend:
   - Fetch into a folder **outside** the repository (raw stays out; `sources/batas-wilayah/SOURCE.txt` keeps
     `content_sha256` per regency, only Kudus's raw file stays as a sample): `fetch <raw_dir> <regency>` with
     `xargs -P 4` (≈ 5 min for Jateng); copy `sources/batas-wilayah/33.19.json.gz` in or refetch Kudus.
   - `build <raw_dir> data/wilayah/wilayah.json.gz data/batas-wilayah` (≈ 30 s for Jateng on 4 CPUs, one regency per
     worker, `--workers=N`). Always build every regency of the set together. Pass 2 ended after 2 rounds with 0
     differing border arcs. Then `tools/data-check --write`.
   - Checks done for Jateng (2026-11-27): every village of `wilayah` 33.* has a polygon; 0 proper crossings among
     820,501 village segments of the whole province (also across regencies); no edge used twice in one direction;
     district areas equal BIG's BATAS_KECAMATAN_AR to 4 decimals in 574/576 (33.01.24 and 33.17.09 differ by exactly
     BIG's undefined areas); Kudus's area and status numbers unchanged and its files byte-identical when built alone;
     a full-precision build (`--tolerance=0`, what `presisi` does) of Jateng passes the same checks (6.5 min; 285 arcs
     and 42 junctions in 265 villages keep more than 6 decimals; pass 2 ended after 2 rounds). `tools/checks/batas-wilayah.py` (session 2, PR #29) on
     the 11 m build with `--big`: everything passes except 7 known cases, none a defect of the data: 3 "holes" that
     are enclaves of another regency of the folder (Kota Magelang in 33.08, Kota Salatiga in 33.22, one of the 5 parts
     of Badran 33.22.03.2001 in 33.09; the checker looks at one regency at a time), 2 districts whose BIG area
     includes an undefined area (33.01.24, 33.17.09), and 2 borders (33.24–33.74, 33.28–33.76) where BIG's own lines
     of the two regencies do not coincide (under 1 m apart in BIG, not shared arcs, so simplified separately, up to
     11.4 m apart). On the full-precision copy the checker fails only on the same 3 enclaves and notes 7 places where
     BIG's lines differ (≤ 0.94 m). Possible follow-ups for the checker's owner: count holes filled by another
     regency of the folder as covered; subtract undefined areas before `--big`.
8. Later (in app repositories, not here): SPMB `check-app` adapter, SPMB income list migration (F-024), SPMB data
   via `fondasi-sync`.

## Blockers / waiting on

- Hosts blocked from cloud sessions: `jateng.kemenag.go.id` (times out since 2026-11-25; R-06 brief), `kemenag.go.id` (refused), `jdih.kemendagri.go.id` (no answer, 2026-11-26), `emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`, `kurikulum.kemendikdasmen.go.id`
  (and `disdikbud.jatengprov.go.id`, replaced by `pdk.jatengprov.go.id`) → browser briefs.
- R-10b leftovers (PASI U14/U16, POPNAS handbook): the 2026-11-27 browser run found no official copy; see
  `sources/atletik/R-10b-SOURCE-2026-11-27.txt` for every place searched. PASI's real domain is www.pbpasi.org
  (the brief tried pasi.or.id); a cloud session can search it directly.
- The Claude GitHub App may need access to the renamed repository for PR notifications (GitHub → Apps → Claude).

## Session log (newest first, keep the last 10)

- 2026-11-28 · session data-round 8 · `pw/practical-thompson-r2to0p` — R-11 `atletik-rekor` (user: use the championships as they are): PASI tables found at www.pbpasi.org (senior, U20, U18; 170 records with 19 errata), World Athletics world/U20/U18/Asian lists rendered in Chromium (415 records), Wikipedia only as cross-check (26 differences); F-037 (holders with birth dates as published).
- 2026-11-27 · session data-round 7 (account A) · `nty/magical-ramanujan-54d9nu` — R-10b delivered by the user's browser run: POPDA Jateng 2026 juknis read on page images into `atletik-nomor`/`atletik-kelompok-umur` 2026-11-27 (20 events per sex, implements, entry rules, "24 kg" erratum unresolved), POPNAS age rule secondary; PASI and POPNAS handbook not found. R-06/R-14 uploads held only search records (stored).
- 2026-11-27 · session data-round 7 (account A) · `nty/magical-ramanujan-54d9nu` — PR #31: `batas-wilayah` stays at Jawa Tengah (user). Next step R-10b checked from the cloud: official PASI/POPDA/POPNAS sources not reachable or not published there; waits for the user's browser run of brief R-10b.
- 2026-11-27 · session data-round 7 (account A) · `nty/magical-ramanujan-54d9nu` — R-18 Jawa Tengah: 35 regencies fetched (4 workers, outside the repo), blocker solved (34 rings crossed only after rounding to 6 decimals, none in BIG; the halving refined whole rings and pass 2 ping-ponged border arcs), converter refines only crossing arcs, carries refinements between rounds, checks collapsed rings and arc-vs-arc crossings, extra decimals for arcs and junctions, parallel build; `batas-wilayah` covers 8,563 villages. Session 2 (account B) works on the checker.
- 2026-11-27 · akun-2 · `pw/exciting-goldberg-mqpkx5` — R-18 support: `tools/checks/batas-wilayah.py` (coverage, district = union of villages, holes, cross-regency borders, `--big` district areas, `--render` SVG; parallel per regency) tested on Kudus and on Kudus+Pati+Jepara built outside the repo (simplified and full precision; BIG's own full-precision borders differ by < 0.5 m at two tri-junctions, reported as notes); docs/data.md "Using boundaries in apps"; `fondasi-data` line. For the Jateng build: run the check on the output with `--big --render`.
- 2026-11-27 · session data-round 6 · `nty/eloquent-davinci-myz72i` — PR #28: `presisi` (servers fetch full precision from BIG, user's choice), merged main (PR #27, F-036). Jawa Tengah started: 35 regencies fetched (65 MB, outside the repo), converter got cross-regency topology and crossing refinement; build blocked by a ring that crosses itself at full precision. Handed over.
- 2026-11-27 · session data-round 6 · `nty/sekolah-koordinat` — R-17: 539,580 detail pages crawled (20 → 40 workers → 160 threads, F-029 without fixed cap), coordinates merged into `sekolah` 2026-11-27 (84.4 % with a pair, 1,222 sign/swap fixes, 7 default pairs null, F-036); sinaubareng cross-check 2,136/2,148 identical. PR open.
- 2026-11-27 · session data-round 6 · `nty/eloquent-davinci-myz72i` — Boundary sources researched (BIG Edisi Juni 2026 best: Kemendagri codes, 99.7 % of villages; GADM/OSM/HDX rejected); F-035; `batas-wilayah` 2026-06-15 for Kudus (±11 m, shared arcs, district areas equal BIG). Then `presisi` for servers (fetch from BIG, checked against `content_sha256`; user chose this over Drive/R2). Next: more regencies on demand.
- 2026-11-27 · session data-round 5 · `nty/kerangka-tka-atribusi` — PR #24 merged. F-034 (third-party works for education with credit); attribution added to every `kerangka-tka` stimulus. Next: R-17.
- 2026-11-27 · session data-round 5 · `nty/kerangka-tka-contoh-soal` — PR #23 merged. `kerangka-tka`: 24 sample questions of 047 with 13 figures (keys recomputed, 4 errata) and the 2026 category limits marked secondary (F-033). Next: R-17.
