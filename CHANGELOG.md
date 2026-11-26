# Changelog

All notable changes ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/)).

## [Unreleased]

### Added
- Athletics sets `atletik-nomor`, `atletik-kelompok-umur`, `atletik-hasil` 2026-03-20 (R-10) from World Athletics rules
  and the combined-events scoring tables, converter `tools/converters/atletik.py` with scoring checks (F-027).
- `tools/converters/sekolah.py`: resumable crawler (Dikdas, Dikmen, PAUD, Dikmas) and converter for
  referensi.data.kemendikdasmen.go.id that matches regions to `wilayah` by name, with spelling rules that never guess
  between several candidates (R-01).
- Decision F-028: which forms and regions `sekolah` keeps.

### Changed
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
