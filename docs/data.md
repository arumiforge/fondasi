# Shared data: how it works (F-003)

## Layout of a set

```
data/<set>/
  manifest.json     version (YYYY-MM-DD, the source's date), description, status, source, licence, counts, fields
  SHA256SUMS        checksum of every other file (tools/data-check --write)
  <files>           gzipped JSON (large lists, one file per province where useful) or plain JSON (small lists)
```

- Field names are short and stable; labels keep the official Indonesian spelling. Codes are the official ones
  (Kemendagri region codes, NPSN, Dapodik reference IDs) — never invented. Where an official code is not yet
  verified, the set stays `planned`.
- A converter in `tools/converters/` (or a written procedure in the manifest when the source is a PDF or a
  page) rebuilds the set from the source. Sources are untrusted: parse with strict patterns, never execute.
- `tools/data-check` (CI) verifies every manifest and checksum.

## Changing a set

1. Put the raw source outside the repository (or in `sources/<set>/` when it is small and its licence allows).
2. Run the converter; check counts against the source; bump `version`.
3. `tools/data-check --write`, then `tools/data-check`.
4. `CHANGELOG.md` line; commit `feat(data): <set> <version>`; PR.

## Using a set in an app (any stack)

```bash
FONDASI_DIR=/path/to/fondasi /path/to/fondasi/tools/fondasi-sync wilayah     # copies data/wilayah at Fondasi's HEAD
/path/to/fondasi/tools/fondasi-sync sekolah 3f2c1a9                          # or at a given commit/tag
/path/to/fondasi/tools/fondasi-sync --check                                  # CI in the app: copies untouched
```

The app gets `data/fondasi/<set>/` and a line in `fondasi.lock` (`<set> <version> <commit>`), commits both and
imports the files with its own importer, keyed on the manifest version (re-import only when it changes; SPMB's
`referensi:import --bawaan` is the model). In a Claude cloud session, attach Fondasi first
(`add_repo arumiforge/fondasi`, cloned at `/home/user/fondasi`); `fondasi-sync` finds it there.

## Full-precision boundaries on a server (`batas-wilayah`, F-035)

`data/batas-wilayah` carries boundaries simplified to about 11 m, which is enough for maps and filters. Full
precision (about 0.1 m; ≈ 0.5 MB per regency, ≈ 370 MB gzipped for Indonesia) is not stored in Fondasi or anywhere
else: the server fetches it from BIG itself, and Fondasi only pins which content is expected.

```bash
git -C /opt/apps/_fondasi pull
python3 -I /opt/apps/_fondasi/tools/converters/batas-wilayah.py presisi /opt/apps/<app>/<env>/data/batas-wilayah 33.19
```

- It fetches each regency from `geoservices.big.go.id` (the server must reach it; seconds per regency), compares
  the content with `content_sha256` in Fondasi's `data/batas-wilayah/manifest.json`, then writes
  `desa/<regency>.geojson.gz`, `kecamatan/<regency>.geojson.gz`, the raw download in `raw/`, `manifest.json`
  (every regency with `matches_fondasi`) and `SHA256SUMS`. Same fields as the simplified set.
- It refuses a regency Fondasi does not list yet, or one BIG has changed since Fondasi was built: add or refresh
  that regency in Fondasi first (`fetch` + `build`, PR), pull, and run again. `--accept-new` overrides this for an
  urgent case; the manifest then shows `matches_fondasi: false` and Fondasi must be updated afterwards.
- Needs only `python3` (present on Ubuntu servers). Mount the folder read-only into the app container, or import it
  with the app's importer keyed on `manifest.json` → `regencies[].content_sha256`. The folder can be rebuilt at
  any time, so it needs no backup.

## Getting data from sources this environment cannot reach

Some sources (EMIS, PDDikti, Disdikbud Jateng, the curriculum site) are blocked from cloud sessions. They are
fetched in a **Claude in Chrome** session on the developer's computer, following a brief in
[data-requests.md](data-requests.md): the browser session saves the raw files, the developer drops them into a
cloud session (or commits them to `sources/<set>/` on a branch), and a cloud session runs the converter.
