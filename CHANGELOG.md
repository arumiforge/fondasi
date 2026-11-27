# Changelog

All notable changes ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/)).

## [Unreleased]

### Added
- `atletik-nomor` and `atletik-kelompok-umur` 2026-11-27 (R-10b): POPDA Tingkat Provinsi Jawa Tengah 2026 from the
  Dispora Jateng juknis (letter 400.3.9.2/371/2026, scanned, read on the page images): 20 events per sex across SD,
  SMP and SMA (new event codes 80m, 1000m, 3000mW, TriSD), shot and javelin weights per level, at most two
  individual events per athlete, Trilomba and quota limits, the exhibition rule (fewer than 5 kabupaten/kota) and the
  medal-based overall standing; eligibility born in 2008 or later ("tahun kelahiran maksimal 2008"). The SMA putri
  shot is printed "24 kg": stored as null with an unresolved erratum (F-031). POPNAS age rule (at most 18) added as
  secondary, quoted by Kemenpora from Peraturan Ketua Umum PP BAPOPSI 8/2022. PASI U14/U16 and the POPNAS athletics
  handbook were not reachable on an official site (pasi.or.id does not resolve).
- Search records of the 2026-11-27 browser runs: `sources/atletik/R-10b-SOURCE-2026-11-27.txt`,
  `sources/kaldik-madrasah-jateng/R-06-SEARCH-2026-11-27.txt` (no official copy of the Dirjen Pendis guideline
  4860/2026 or the Kanwil decree online) and `sources/wilayah/R-14-SOURCE-ditjenbinaadwil-2026-11-27.txt` (the
  official file URL of Kepmendagri 300.2.2-2430/2025 on the Ditjen Bina Adwil site).
- `batas-wilayah` 2026-06-15 now covers all of Jawa Tengah (R-18, F-035; user, 2026-11-27): 35 regencies, all 8,563
  villages of `wilayah` 33.* and all 576 districts, 6.1 MB. Borders between regencies are identical on both sides
  (1,792 shared border arcs); no two villages overlap and no ring crosses itself (0 crossings among 820,501
  segments). District areas equal BIG's BATAS_KECAMATAN_AR to four decimals in 574 of 576 districts; 33.01.24 and
  33.17.09 differ by exactly BIG's undefined areas (0.0968 and 0.0052 km², an island without a village). Kudus
  keeps its numbers (areas, statuses); its border arcs with Jepara, Demak, Pati and Grobogan are now cut at the
  same points as theirs. Full-precision downloads stay outside the repository; `sources/batas-wilayah/SOURCE.txt`
  lists the fetch time and `content_sha256` of every regency, and `33.19.json.gz` stays as a sample. `tools/checks/batas-wilayah.py --big`
  passes except for enclaves counted as holes (Kota Magelang, Kota Salatiga, a part of Badran), the two undefined
  areas and two borders where BIG's own lines do not coincide (33.24–33.74, 33.28–33.76; under 1 m apart in BIG).
- `tools/checks/batas-wilayah.py <data_dir> [--big] [--render <out_dir>]` (R-18, F-035): checks a `batas-wilayah`
  build (Fondasi's, a converter build elsewhere, or a server's `presisi` copy) — every village and district of
  `data/wilayah` in each listed regency has a polygon, each district is exactly the union of its villages (same
  directed edges, same area, `area_km2` fields agree), no holes beyond BIG's undefined areas, borders between
  neighbouring regencies identical point for point; `--big` compares district areas with BIG's
  `BATAS_KECAMATAN_AR` (`LUASWH`, km²) to 4 decimals; `--render` writes SVGs per regency and for the province
  (dashed where "Batas Indikatif"). Exit code 1 on failure; one worker per CPU. Tested on Kudus and on Kudus, Pati
  and Jepara built together (simplified and full precision: all 46 districts equal BIG to 4 decimals, the 921
  shared border edges of the simplified build identical) and on broken copies (missing village, wrong area, a
  border point moved 3 m, Kudus built alone next to its neighbours).
- `docs/data.md` "Using boundaries in apps": when ±11 m is enough and when to use `presisi`, showing the boundary
  status (UU 4/2011 Pasal 16 ayat (2): only "Batas Definitif" solid, never a legal boundary), the credit "Sumber:
  Badan Informasi Geospasial", "which village is this point in" as a suggestion users can correct, file sizes per
  regency, loading gzipped GeoJSON in Leaflet and MapLibre.
- `batas-wilayah`: servers build full-precision boundaries themselves with `batas-wilayah.py presisi <out_dir>
  <regency...>` (fetch from BIG, check against the new `content_sha256` per regency in the manifest, build at about
  0.1 m with `SHA256SUMS`); it refuses regencies Fondasi does not list or BIG has changed unless `--accept-new`
  (F-035, `docs/data.md`).
- `sekolah` 2026-11-27 (R-17, F-036): `lintang`, `bujur`, `koordinat_cek`, `koordinat_perbaikan` and
  `koordinat_sama` for all 539,580 units from their detail pages (`/satpen/detail/<npsn>`). 455,250 units (84.4 %)
  have a pair: 449,014 inside their own regency (or within 5 km; at sea or on small islands the nearest regency),
  4,023 in another regency of their province and 2,213 elsewhere in Indonesia, kept as printed and flagged. 1,222
  lost signs or swapped pairs corrected because the corrected pair lies in the unit's own regency (printed values
  in `coordinate_errata`). Null with a reason: 75,525 printed 0, 1,669 empty, 6,500 on one of 7 default pairs
  shared across regencies (`bawaan`, e.g. -5.443757, 114.421127 for 5,931 units), 636 outside Indonesia.
  Coverage per group: dikdas 96.2 %, dikmen 91.8 %, dikmas 76.8 %, PAUD 71.7 %. Cross-check with sinaubareng
  (Pati, Kudus, Jepara): 2,136 of 2,148 pairs identical. Crawl of 539,580 pages with 160 threads (F-029 now has
  no fixed cap); converter steps `plan`, `coords`, `coords-extract`, `coords-merge`; regency boundaries from
  cahyadsn/wilayah_boundaries (MIT) in `sources/sekolah/batas-wilayah/`.
- Data set `batas-wilayah` 2026-06-15 (R-18, F-035): village and district boundaries of Kabupaten Kudus (132
  villages, 9 districts) from BIG's Basis Data Batas Wilayah Administrasi Edisi Juni 2026, keyed by Kemendagri codes,
  simplified to about 11 m on shared arcs (no gaps between neighbours), districts built as the union of their
  villages (areas equal BIG's district layer); boundary status and basis per village. Converter
  `tools/converters/batas-wilayah.py` (fetch from BIG's REST service, build), full-precision download in
  `sources/batas-wilayah/`.
- `kerangka-tka`: every sample-question stimulus carries an `attribution` (owner and where it was printed) and the
  set an `attribution_rule`; F-034 allows third-party works for education when their owners are credited.
- `kerangka-tka` (R-16): the 24 sample questions of Perka BSKAP 047/H/AN/2025 part IV (stimuli, questions,
  options, statements, keys; formulas in TeX; 13 figures in `contoh-soal/`, every key recomputed, 4 errata) and the
  2026 category limits for SD/MI and SMP/MTs (Kurang < 50, Memadai 50–< 76,67, Baik ≥ 76,67, istimewa ≥ 95),
  marked secondary because they come from press reports of the Pusmendik briefing; the conflicting Medcom report
  for Matematika SMP (33,33 / 56,67) is kept beside them.
- Data set `kerangka-tka` 2026-03-06 (R-16, F-030): TKA framework for SD/MI and SMP/MTs from Perka BSKAP
  047/H/AN/2025 (Bahasa Indonesia: text types and characteristics, reading aspects, 3 competencies with 21
  subcompetencies; Matematika: elements, abilities, 3 cognitive levels with 23 thinking processes, 14 content rows
  with 47 scope items), item types and forms, and from Kepmendikdasmen 56/2026 the test subjects per level (20
  SMA/SMK electives), the schedule with minutes and session times, score ranges, categories and the istimewa
  thresholds. Converter `tools/converters/kerangka-tka.py` checks every text unit and table cell against the PDFs;
  3 printing errors in errata.
- `capaian-pembelajaran` 2026-06-11 (R-15, F-032): special-education religion CP for the six religions, phases A–F
  for SDLB/SMPLB/SMALB (Kepka BKPDM 020/2026 Lampiran II, 6 subjects, 192 outcomes, 11 printed "–" without CP) in
  `pendidikan-khusus-agama.json.gz`; transcription `transkripsi-020/2.1-islam.txt` … `2.6-khonghucu.txt` read line by
  line against the page images (diacritics, pinyin and Chinese characters on zoomed crops). Two more printing
  errors in errata. Converter: a table cell continued with `<br>` after a page break keeps its line break, phase
  headings may end with a full stop, grades in a phase heading are read case-insensitively, a subject's page range
  counts every page marker. The set is now complete (305 subjects, 2,816 outcomes).
- `capaian-pembelajaran` 2026-06-11 (R-15, F-032): Pendidikan Agama dan Budi Pekerti for the six religions, phases
  A–F (Kepka BKPDM 020/2026 Lampiran I, 6 subjects, 192 outcomes) in `agama.json.gz`. 020 is a scan: checked
  transcription in `sources/capaian-pembelajaran/transkripsi-020/` (OCR draft, every line read against the page
  images), converter `tools/converters/capaian-pembelajaran-agama.py` with an OCR diff and a comparison with
  sinaubareng's SD transcription (96 of 96 identical); 7 printing errors listed as errata. `index.json` is now built
  from the files present.
- Data set `capaian-pembelajaran` 2025-11-28 (R-15, F-030, F-032): learning outcomes for 293 subjects (549 phases,
  2,432 outcomes) from Kepka BSKAP 046/H/KR/2025 Lampiran I–V (PAUD, general subjects, SMK, kesetaraan, special
  education) and SK Dirjen Pendis 9941/2025 (madrasah), with rasional, tujuan, karakteristik, element tables and
  source pages; 9 errata (F-031) and per-subject `source_notes`. Religion CP (Kepka BKPDM 020/2026) follows in a
  second, checked step. Converter `tools/converters/capaian-pembelajaran.py` is reproducible and stops on structure
  problems.
- Data set `mapel` 2025-09-22 (R-08): subjects and JP per year for every level and grade, from Permendikdasmen
  13/2025 Lampiran II (Tabel 1–29: SD, SMP, SMA, SMK 3/4-year, SDLB, SMPLB, SMALB, Paket A/B/C) and KMA 1503/2025
  (25 madrasah tables: MI, MTs, MA, MAK, MILB, MTsLB, MALB, read from page images), with electives, phases,
  footnotes, implementation rules and errata. Converter `tools/converters/mapel.py` checks all 144 printed totals.
- Decision F-031: printed errors in official tables (store the value the totals require, keep the printed one,
  list it in `errata`); Bahasa Inggris transition (Pasal 33) for SD/MI only.
- Audit of the data in the app repository sinaubareng (`docs/sinaubareng-audit.md`) and decision F-030: curriculum
  regulations copied to `sources/mapel/`, `sources/capaian-pembelajaran/`, `sources/kerangka-tka/`; sets `mapel`
  (all levels), `capaian-pembelajaran`, `kerangka-tka` and school coordinates planned (R-08, R-15, R-16, R-17).
- Athletics sets 2026-11-26 (R-10b, O2SN part): O2SN 2026 eligibility groups for SD/MI, SMP/MTs and SMA/MA/SMK/MAK
  (birth date limit, grades), Kids' Athletics events (Kanga Escape, Formula 1) with their courses, SMP Trilomba and
  SMA/SMK Pancalomba (events, implements, trials, qualifying marks) with PDF page references, and their scoring: the
  linked tables are World Athletics formulas (SMP capped at 1500; the women's 60 m parameters were derived from the
  table), all 17,595 printed rows checked with `atletik.py --tables`. Guides and tables kept in `sources/atletik/o2sn/`.
- Athletics sets `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil` 2026-03-20 (R-10) from World Athletics rules
  and the combined-events scoring tables, converter `tools/converters/atletik.py` with scoring checks (F-027).
- `tools/converters/sekolah.py`: resumable crawler (Dikdas, Dikmen, PAUD, Dikmas) and converter for
  referensi.data.kemendikdasmen.go.id that matches regions to `wilayah` by name, with spelling rules that never guess
  between several candidates (R-01).
- Decision F-028: which forms and regions `sekolah` keeps.


### Changed
- `batas-wilayah.py build`: one regency per worker (`--workers`, default every CPU; Jawa Tengah in about 30 s on 4
  CPUs). Rings that crossed themselves only because of rounding to 6 decimals (34 in Jawa Tengah, none in BIG's own
  data) no longer stop the build: only the arcs that cross are refined (half the tolerance, every point, then up to
  9 decimals for those arcs and their junctions), every pass-2 round continues from the arcs refined so far (it used
  to refine the same border arcs again and never converged), collapsed rings (an edge used twice, no area) and arcs
  of different rings that cross are refined too, and arcs shorter than 0.1 m no longer break district rings.
  Full-precision builds (`presisi`) go through the same checks. Errors name the regency and villages.

### Added
- Data set `kaldik-madrasah-jateng` 2026-06-29 (R-06): madrasah calendar of Jawa Tengah 2026/2027 from Keputusan
  Kakanwil Kemenag Jateng 1681/2026, transcribed in `tools/converters/kaldik-madrasah-jateng.py`, which recomputes
  HK/HL/HE per month (all 12 match) and checks holidays against `libur-nasional`; raw PDF in `sources/`.

### Changed
- `wilayah` checked against Kepmendagri 300.2.2-2430/2025 (R-14): it changes only island data of Aceh and Sumatera
  Utara; region codes, names and counts already match, so the data stays 2026-02-13. The decree is kept in
  `sources/wilayah/`.
- `sekolah` 2026-11-26 (R-01 part 1): every active school of Dikdas and Dikmen in all 38 provinces (283,421: SD, MI,
  SMP, MTs, SMA, MA, SMK, SLB, SPK, Pendidikan Diniyah Formal, Satuan Pendidikan Muadalah, Buddhist, Hindu and
  Christian schools) replaces the SD/MI-only version 2026-11-18. New fields `alamat`, `kode_desa`, `kode_kecamatan`,
  `kode_kabupaten`, `kode_provinsi` (Kemendagri codes of `wilayah`, 97.8 % matched to the village, never invented) and
  `kode_kecamatan_dapodik`. 2,483 SD/MI of the old version are gone because the source marks them merged or closed.
- `sekolah` 2026-11-26 (R-01 part 2, same crawl date): adds every active PAUD unit (TK, KB, RA, TPA, SPS, PAUDQ, SPK
  TK/KB, Buddhist, Hindu and Christian PAUD) and PKBM and SKB: 539,580 units, 98.0 % with village code. The crawler
  takes regency codes, skips Dikmas districts without PKBM or SKB and runs in parallel workers (F-029).

### Added
- Data set `kodepos` 2025-06-30 (R-03): postal code of all 83,762 villages keyed by the `wilayah` codes, from
  cahyadsn/wilayah_kodepos (MIT), converter `tools/converters/kodepos.py` with checks against `wilayah`.
- Data set `libur-nasional` 2026-09-15 (R-04): national holidays and cuti bersama 2026 and 2027 from the SKB 3 Menteri,
  one row per day, transcribed by `tools/converters/libur-nasional.py` with weekday checks; raw PDFs in
  `sources/libur-nasional/`.

### Changed
- `kaldik-jateng` 2026-09-15: every holiday event checked against the SKB (`skb` field); all 2027 estimates match;
  Maulid 2026 differs (SKB: 25 Agustus); SKB days the province did not list are named per year.

### Added
- Data set `kaldik-jateng` (2026/2027 in full, 2025/2026 key dates) from the R-05 browser collection, raw PDFs in
  `sources/kaldik-jateng/`; calendar layers (F-025); briefs R-12 (national calendar) and R-13 (kabupaten/kota).

### Changed
- `skema-siswa`: NISN 10 digits, student NIK required, NIK of the mother and KK number 16 digits; its income list is the shared one (F-024).

### Added
- Decoration without limits made by Codex, pages usable before decoration loads, skeleton loading, unique QR designs
  (F-022); detailed student data in internal school apps (`docs/school-data.md`) and data set `skema-siswa` with its
  converter (F-023).
- Agent workflow for every repository (F-017) with the `app-session` skill template; assets: minify served copies,
  keep originals, version every asset (F-018); AI assistant rules incl. round robin and Gemini (F-019, skill
  `fondasi-ai`); printing on A4/F4, unique QR codes with a centred logo, visitor statistics (F-020, web baseline
  §11–12); guide pages in the GitHub Docs "Get started" pattern (F-021, skill `fondasi-guides`).
- Adopting Fondasi in any repository (F-016): `docs/adopting.md` (starter prompt, audit areas, report format, base
  setup), skill `fondasi-adopt`, templates `templates/repo/CLAUDE.md`, `docs/progress.md`, `docs/decisions.md`.

### Changed
- `server/check.sh` is app-neutral (F-015): no SPMB section; apps plug in with `/opt/apps/<app>/check-app`
  (template `server/templates/check-app`); states S2 (ready), S3 (an app needs attention), S9 (every app answers);
  `APPS_ROOT` (old `SPMB_ROOT` still accepted).

### Added
- Feedback standard (F-014): `docs/feedback.md` (tiers 0–5, placement on desktop and phone, copy, accessibility, audit
  checklist) and skill `fondasi-feedback` (apply, audit, PRD).
- Server: `setup.sh` and `check.sh` from SPMB (D-112), app-neutral (apps read from `/opt/apps/PORTS` with an
  optional hostname column, SPMB section only where SPMB exists, `SERVER_NAME` label); compose template.
- Rules: server playbook, app contract, several servers (F-008), settings and Turnstile (F-005), storage (F-006).
- Data framework (F-003): `tools/fondasi-sync` (data sets and skills, `fondasi.lock`, `--check`),
  `tools/data-check`; sets `wilayah` 2026-02-13, `sekolah` 2026-11-18 (SD/MI), `tahun-ajaran` 2026-11-25;
  catalogue of planned sets (F-007) and browser data-request briefs.
- Skills: `fondasi-session`, `fondasi-server`, `fondasi-data`, `bahasa-indonesia-plain` (moved from SPMB).
- Conventions (F-009), UI/UX rules against generic AI-made design (F-010), Codex visual-asset workflow (F-011);
  templates for every repository (`AGENTS.md`, commit hook and CI that also reject Codex/ChatGPT attribution) and the
  `ai/` brief kit; skills `fondasi-ui`, `fondasi-visual`.
- Everything users see is Indonesian, export/import rules (F-012); web app baseline (F-013, `docs/web-baseline.md`,
  skill `fondasi-web`).
- Cloud environment for any Claude account (`.claude/cloud/setup.sh`, variables, hosts).
