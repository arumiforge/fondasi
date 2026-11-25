# Claude cloud environment (any Claude account)

Work happens across several Claude accounts that share nothing but the repositories. Each account sets up its
environments once, as below. Scripts live in the repositories, so changing them here updates every account.
Never put secrets in environment variables of a cloud environment: they are stored in plain text.
Official reference: <https://code.claude.com/docs/en/cloud-environments>.

## Per account, once

1. **GitHub**: connect GitHub in claude.ai with access to the private repositories the account works on
   (`arumiforge/fondasi`, `arumiforge/spmb`, other apps) and make sure the Claude GitHub App is installed on them.
2. **Environments**: one per main repository (the app's own docs say how; SPMB: `docs/cloud-environment.md` in
   `arumiforge/spmb`) plus one for Fondasi work:

| Setting | Fondasi environment |
| --- | --- |
| Name | `Fondasi` |
| Repositories | `arumiforge/fondasi` |
| Network access | Limited with "Allow package managers", plus the hosts below (or Full) |
| Environment variables | see below |
| Setup script | `if [ -f fondasi/.claude/cloud/setup.sh ]; then bash fondasi/.claude/cloud/setup.sh; elif [ -f server/.claude/cloud/setup.sh ]; then bash server/.claude/cloud/setup.sh; fi` |

App environments that use shared data or rules can add `arumiforge/fondasi` as a second repository, or attach it
during a session (`add_repo`).

## Environment variables (no secrets)

| Variable | Value | Used by |
| --- | --- | --- |
| `TZ` | `Asia/Jakarta` | dates in logs and data versions |
| `FONDASI_DIR` | `/home/user/fondasi` | `tools/fondasi-sync` in app sessions (it also looks there by default) |
| `ARUMI_ACCOUNT` | a neutral label of the account, e.g. `akun-1`, `akun-2` | session labels in `docs/progress.md` (never an email or a name) |
| `ARUMI_GIT_NAME` / `ARUMI_GIT_EMAIL` | `Arumi Studios` / `arumiforge@gmail.com` | the session skills set git identity from them (identity is not a secret) |

Per-account differences that cannot live in a repository (which repositories GitHub grants, network hosts,
installed tools) go into the *Blockers* of `docs/progress.md` when they block work.

## Hosts for Limited network access

| Host | Why |
| --- | --- |
| `github.com`, `raw.githubusercontent.com`, `codeload.github.com`, `objects.githubusercontent.com` | Fondasi and app repositories; cahyadsn region/postal sources |
| `dapo.kemendikdasmen.go.id`, `referensi.data.kemendikdasmen.go.id`, `sekolah.data.kemendikdasmen.go.id` | School data (R-01) |
| `www.kemenkopmk.go.id`, `jateng.kemenag.go.id` | National holidays (R-04), madrasah calendar (R-06) |
| `worldathletics.org` | Athletics rules (R-10) |

Blocked from cloud sessions at the time of writing (use a browser session, [data-requests.md](data-requests.md)):
`emis.kemenag.go.id`, `pddikti.kemdiktisaintek.go.id`, `disdikbud.jatengprov.go.id`, `kurikulum.kemendikdasmen.go.id`.
