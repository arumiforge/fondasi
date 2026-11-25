# Pointer block for app repositories

Paste this block into every app's `CLAUDE.md` (adapt the first line). It is how a Claude session in that app
finds the shared rules without the user explaining them again.

```markdown
## Fondasi (shared rules, data and skills)

This app follows `arumiforge/fondasi` (Arumi Studios' shared foundation). When the work touches the server or
deploys, file storage (S3/R2), integration settings (env vs panel, Turnstile), shared reference data (regions,
schools, calendars, Dapodik lists, athletics) or Indonesian user-facing text: attach the repository
(`add_repo arumiforge/fondasi`), read its `CLAUDE.md` and follow its skills (`fondasi-server`, `fondasi-data`,
`bahasa-indonesia-plain`). Its decisions (`F-…`) apply here unless this repo records an exception.
Shared data and skills are copied with `tools/fondasi-sync` (`fondasi-sync <set>`, `fondasi-sync skill bahasa-indonesia-plain`; versions in `fondasi.lock`), never edited by hand.
```
