---
name: fondasi-server
description: Prepare, check and change any Arumi Studios VPS and the Docker apps on it (any stack) — check.sh state, setup.sh on fresh or busy servers, the app contract, ports, Cloudflare Tunnel routes, several servers, storage and settings rules. Use for any server, deploy, compose, tunnel, storage (S3/R2) or env-vs-panel question, in Fondasi or in an app repository.
---

# Server work

1. **Ask for the state first.** Get the output of `sudo bash /opt/apps/_fondasi/server/check.sh` (or
   `bash check.sh` uploaded to a new server; an app may wrap it, e.g. SPMB's `spmb check`). Its State/Next/Needs attention block replaces
   re-explaining the server. Which server? `docs/servers.md`.
2. Keep Fondasi app-neutral (F-015): app-specific checks go into the app's `check-app` adapter
   (`server/templates/check-app`), never into `server/check.sh`.
3. Follow `docs/server-playbook.md` for the server and `docs/app-contract.md` for apps; compose files start from
   `server/templates/app.compose.yaml`.
4. Settings: `docs/settings.md` (standard env names, environment wins over the panel, Turnstile).
   Files: `docs/storage.md` (VPS disk default, S3-compatible optional, public-sector personal data in Indonesia).
5. Never break what runs: `check.sh` stays read-only; `setup.sh` keeps Docker packages, merges `daemon.json`,
   never restarts Docker while containers run, never switches ufw on over unlisted public services; SSH port
   always open, password login off only after a proven key, sshd reloaded never restarted, no network config edits.
6. No IPs, ports, secrets, tokens or emails in any repository; new rules go into the docs here and `decisions.md`.
7. After changing a script: `bash -n`, `shellcheck`; test `check.sh` against a fake layout with `APPS_ROOT=<dir> OFFLINE=1`.
