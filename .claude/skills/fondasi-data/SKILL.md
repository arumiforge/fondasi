---
name: fondasi-data
description: Add, update or use Fondasi's shared public data (regions, schools of every level, postal codes, holidays and education calendars, Dapodik reference lists, curriculum subjects, universities, athletics events/age groups/results/records) and copy it into an app with fondasi-sync. Use whenever an app needs such data or a set must be refreshed.
---

# Shared data

- Catalogue and status: `data/README.md`. How sets are built and versioned: `docs/data.md`.
- Using a set in an app: `tools/fondasi-sync <set> [ref]` from the app root, commit `data/fondasi/<set>` and
  `fondasi.lock`, import with the app's own importer keyed on the manifest version. Never edit copied files.
- Building or refreshing a set: only public data without personal data; official codes only (no invented codes —
  unverified sets stay `planned`); converter in `tools/converters/` or a written procedure; bump the version
  (the source's date); `tools/data-check --write` then `tools/data-check`; CHANGELOG line.
- Sources blocked from cloud sessions: write or follow a brief in `docs/data-requests.md` for a Claude in Chrome
  session; it collects raw files with `SOURCE.txt`, a cloud session converts them.
- Licences go into `THIRD_PARTY_NOTICES.md`; ask before anything other than public government data,
  MIT/BSD/Apache/ISC/CC-BY.
