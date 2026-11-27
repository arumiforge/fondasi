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
| `nty/eloquent-davinci-myz72i` | session data-round 6 | R-18 `batas-wilayah`: PR #26 merged (Kudus); PR #28 `presisi` + cross-regency topology; Jawa Tengah handed over (see Next steps 7) | PR #28 open |
| `nty/sekolah-koordinat` | session data-round 6 | R-17 latitude/longitude for every unit of `sekolah` (F-036) | PR #27 merged |
| `pw/exciting-goldberg-mqpkx5` | akun-2 | R-18 support: `tools/checks/batas-wilayah.py` (coverage, areas, cross-regency arcs, `--big`, `--render`), docs/data.md "Using boundaries in apps", `fondasi-data` line. Does not touch the converter or `data/batas-wilayah/` | PR open |

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
   when an official document states them. **R-17 done** (`sekolah` 2026-11-27, F-036): coordinates of every unit from `/satpen/detail/<npsn>`. To refresh:
   `python3 -I tools/converters/sekolah.py coords data/sekolah <raw outside the repo> sources/sekolah/koordinat
   --threads=160` (≈ 7 h for 540,000 pages; resumable; delete the TSVs first for a new crawl), then `coords-merge
   data/sekolah sources/sekolah/koordinat sources/sekolah/batas-wilayah <date>` and `tools/data-check --write`.
   A list refresh (`build`) drops the coordinate fields: run `coords-merge` after it.
5. When the user uploads R-12 or R-02/R-07/R-09 zips: verify SHA-256, keep raw files in `sources/<set>/`,
   build the set.
6. `wilayah` / `kodepos`: **current** (R-14 done 2026-11-26). Kepmendagri 300.2.2-2430/2025 changes only island
   data (four islands move to Aceh Singkil); `data/wilayah` 2026-02-13 matches its region totals exactly, and
   `kodepos` is unaffected. Check again when Kemendagri publishes a new decree on region codes (cahyadsn usually
   follows within months; compare the header of `db/wilayah.sql`).
7. **R-18 `batas-wilayah`** (F-035): Kudus done (PR #26). **Now: all of Jawa Tengah (user, 2026-11-27: "tambahkan
   juga untuk seluruh jawa tengah")**, 35 regencies 33.01–33.29, 33.71–33.76 (8,563 villages).
   - Fetch into a folder **outside** the repository (≈ 65 MB raw for Jateng; the repository keeps only
     `content_sha256` per regency, servers fetch full precision themselves): `fetch <raw_dir> <regency>` with
     `xargs -P 4` takes ≈ 5 min. Copy `sources/batas-wilayah/33.19.json.gz` in too, or refetch Kudus.
   - Then `build <raw_dir> data/wilayah/wilayah.json.gz data/batas-wilayah` (≈ 4 min for Jateng). The converter now
     builds all regencies in the folder with one topology across regency borders: pass 1 finds the points where
     neighbouring regencies must cut their border arcs; pass 2 repeats until both sides of every shared border
     arc are simplified identically (arcs a regency had to keep finer are forced finer in its neighbour); pass 3
     writes the files. Rings that cross themselves after simplification get their arcs' tolerance halved (to 0 =
     every point) — this is in place and leaves Kudus byte-identical.
   - **Open blocker**: the Jateng build stops in pass 2 round 2 with "a ring crosses itself even at full
     precision". Find the ring (print its code and regency in `Topology.simplify`): either BIG's own ring touches
     or crosses itself (then accept rings that already cross at full precision: compare with the unrounded source,
     skip the check for them and list them in the manifest), or rounding to 6 decimals creates the crossing (then
     keep that arc unrounded or use 7 decimals for it). Round 1 had 17 differing shared border arcs, round 2 had 7:
     check that the rounds converge once the blocker is solved.
   - Afterwards: check no village of data/wilayah 33.* lacks a polygon (BIG had all 8,563), compare district areas
     with BIG's BATAS_KECAMATAN_AR (Kudus matched to 4 decimals), render a picture, update the manifest notes,
     `data/README.md` row, CHANGELOG, SOURCE.txt (hashes per regency), F-035 text (raw kept outside the repository
     for many regencies; delete `sources/batas-wilayah/33.19.json.gz` or keep it as the sample), PR, merge (F-026).
8. Later (in app repositories, not here): SPMB `check-app` adapter, SPMB income list migration (F-024), SPMB data
   via `fondasi-sync`.

## Blockers / waiting on

- Hosts blocked from cloud sessions: `jateng.kemenag.go.id` (times out since 2026-11-25; R-06 brief), `kemenag.go.id` (refused), `jdih.kemendagri.go.id` (no answer, 2026-11-26), `emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`, `kurikulum.kemendikdasmen.go.id`
  (and `disdikbud.jatengprov.go.id`, replaced by `pdk.jatengprov.go.id`) → browser briefs.
- The Claude GitHub App may need access to the renamed repository for PR notifications (GitHub → Apps → Claude).

## Session log (newest first, keep the last 10)

- 2026-11-27 · akun-2 · `pw/exciting-goldberg-mqpkx5` — R-18 support: `tools/checks/batas-wilayah.py` (coverage, district = union of villages, holes, cross-regency borders, `--big` district areas, `--render` SVG; parallel per regency) tested on Kudus and on Kudus+Pati+Jepara built outside the repo (simplified and full precision; BIG's own full-precision borders differ by < 0.5 m at two tri-junctions, reported as notes); docs/data.md "Using boundaries in apps"; `fondasi-data` line. For the Jateng build: run the check on the output with `--big --render`.
- 2026-11-27 · session data-round 6 · `nty/eloquent-davinci-myz72i` — PR #28: `presisi` (servers fetch full precision from BIG, user's choice), merged main (PR #27, F-036). Jawa Tengah started: 35 regencies fetched (65 MB, outside the repo), converter got cross-regency topology and crossing refinement; build blocked by a ring that crosses itself at full precision. Handed over.
- 2026-11-27 · session data-round 6 · `nty/sekolah-koordinat` — R-17: 539,580 detail pages crawled (20 → 40 workers → 160 threads, F-029 without fixed cap), coordinates merged into `sekolah` 2026-11-27 (84.4 % with a pair, 1,222 sign/swap fixes, 7 default pairs null, F-036); sinaubareng cross-check 2,136/2,148 identical. PR open.
- 2026-11-27 · session data-round 6 · `nty/eloquent-davinci-myz72i` — Boundary sources researched (BIG Edisi Juni 2026 best: Kemendagri codes, 99.7 % of villages; GADM/OSM/HDX rejected); F-035; `batas-wilayah` 2026-06-15 for Kudus (±11 m, shared arcs, district areas equal BIG). Then `presisi` for servers (fetch from BIG, checked against `content_sha256`; user chose this over Drive/R2). Next: more regencies on demand.
- 2026-11-27 · session data-round 5 · `nty/kerangka-tka-atribusi` — PR #24 merged. F-034 (third-party works for education with credit); attribution added to every `kerangka-tka` stimulus. Next: R-17.
- 2026-11-27 · session data-round 5 · `nty/kerangka-tka-contoh-soal` — PR #23 merged. `kerangka-tka`: 24 sample questions of 047 with 13 figures (keys recomputed, 4 errata) and the 2026 category limits marked secondary (F-033). Next: R-17.
- 2026-11-26 · session data-round 5 · `nty/kerangka-tka` — PR #22 merged (religion CP Lampiran II, R-15 complete). R-16 `kerangka-tka` built from 047 and 56/2026 (4 frameworks, every text unit and table cell checked against the PDFs, schedule read on the page images, 3 errata). Next: R-17.
- 2026-11-26 · session data-round 5 · `nty/cp-agama-pendidikan-khusus` — 020 Lampiran II transcribed from page images (2.1–2.6, 192 outcomes, every pinyin/diacritic line on zoomed crops, OCR diff clean), `pendidikan-khusus-agama.json.gz` built, `capaian-pembelajaran` complete (305 subjects, 2,816 outcomes). Next: R-16 `kerangka-tka`.
- 2026-11-26 · session data-round 4 · `nty/serene-hamilton-q7whfv` — PR #20 merged (046 + 9941). Religion CP of 020 Lampiran I transcribed from page images (6 religions, 192 outcomes; SD A–C identical to sinaubareng), `agama.json.gz` built, version 2026-06-11. Next: 020 Lampiran II.
- 2026-11-26 · session data-round 4 · `nty/serene-hamilton-q7whfv` — R-15 finished without religion: last SLB section fixed, converter hardened (signature block with NIP cut, PAUD scope tables, SK 9941 merged-cell tables, ligatures, title case, F-031 errata), every outcome checked verbatim against the PDF text; `capaian-pembelajaran` 2025-11-28 built. Next: religion CP (020/2026).
