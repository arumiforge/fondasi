# Changelog

All notable changes ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/)).

## [Unreleased]

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
