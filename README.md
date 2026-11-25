# Fondasi

Shared foundation for every Arumi Studios application (education, athletics, school admission and related
services), whatever its stack. Private; proprietary (`LICENSE`).

| Folder | What |
| --- | --- |
| `server/` | `setup.sh` (prepare a VPS, fresh or already in use), `check.sh` (read-only state + next command), `templates/` |
| `data/` | Public reference data with versions and checksums: regions, schools, academic-year rules… ([catalogue](data/README.md)) |
| `tools/` | `fondasi-sync` (copy a data set or a skill into an app at a pinned version), `data-check`, converters |
| `docs/` | Rules: [server playbook](docs/server-playbook.md), [app contract](docs/app-contract.md), [servers](docs/servers.md), [settings](docs/settings.md), [storage](docs/storage.md), [data](docs/data.md), [conventions](docs/conventions.md), [UI](docs/ui.md), [visual assets](docs/visual-assets.md) — index in [docs/README.md](docs/README.md) |
| `templates/` | `repo/` (AGENTS.md, commit hook, commit-policy CI) and `ai/` (Codex brief kit) for every new repository |
| `.claude/skills/` | Agent skills shared by every repo: `fondasi-session`, `-server`, `-data`, `-ui`, `-visual`, `bahasa-indonesia-plain` |

Apps point to Fondasi from their `CLAUDE.md` ([docs/app-pointer.md](docs/app-pointer.md)) and copy data and skills
with `tools/fondasi-sync`; nothing here is a runtime dependency.
