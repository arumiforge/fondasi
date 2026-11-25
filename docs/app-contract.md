# App contract

Every app on an Arumi Studios VPS follows these rules, whatever its stack (PHP, Node, Python, Go…).
With them, a new app never re-decides the server, and `check.sh` can watch every app the same way.

## Layout and ports

| Rule | Why |
| --- | --- |
| Everything of an app under `/opt/apps/<app>/` (checkout in `src/`, one folder per environment: `staging/`, `production/`) | One place per app; backups and checks know where to look |
| One line per environment in `/opt/apps/PORTS`: `<port> <app>-<env> <public hostname>` | No two stacks share a port; `check.sh` tests the hostname through the tunnel |
| Ports 8100–8199. SPMB takes them from the bottom; other apps from the top (8199, 8198…), skipping any port already listed or used by a container | No collision with SPMB's automatic picking |
| Publish **only** `127.0.0.1:<port>:<container port>` | Docker bypasses ufw; loopback keeps the app private until the tunnel exposes it |
| Compose project `<app>-<env>`, own network and named volumes, its own database container | Stacks never share data by accident; one app's restore never touches another |
| `restart: unless-stopped`, a `healthcheck` on every service, json-file logs with `max-size: 10m`, `max-file: 5` | Survives reboots; `up --wait` knows when it is ready; logs cannot fill the disk |
| Starting point: [`server/templates/app.compose.yaml`](../server/templates/app.compose.yaml) | Already follows every rule above |

## Secrets and settings

- Settings and secrets in a `stack.env` / `.env` next to the compose file, mode `600`, made **on the server**
  (`openssl rand -hex 24`), never in git, never in a chat. Keep a copy of encryption keys in the password manager.
- Integrations use the standard variable names and "environment wins over the panel" ([settings.md](settings.md)).
- Files: VPS disk by default, S3-compatible optional ([storage.md](storage.md)).

## Access from outside

- One tunnel per VPS (F-004): add a *Public Hostname* in the Cloudflare dashboard → `http://127.0.0.1:<port>`
  (always `127.0.0.1`, not `localhost`). Staging and admin-only apps go behind the Access application.
- A separate tunnel only for another client or Cloudflare account: `cloudflared` runs as its own systemd
  unit with its own token, kept on the server.
- Repository access: a read-only deploy key per repository with an SSH alias `github-<app>`; scripts never
  create or read keys.

## Data and backups

- A daily backup per environment (database dump + uploaded files + the env file) into
  `/opt/apps/<app>/<env>/backups/`, kept 14 days, `0600` files in a `0700` folder; one before every deploy.
- Off-site copies: restic to a bucket of its own per app (not the app's file bucket), password in the
  password manager.
- Production personal data never goes to staging.

## Deploys

- Build images from an exact commit (label `org.opencontainers.image.revision`), tag = first 12 characters.
- Staging first; production runs the image that ran on staging.
- Keep the previous image for a one-command rollback; migrations are not rolled back — restore the backup.

## Adding an app, step by step

```bash
sudo bash /opt/apps/_fondasi/server/check.sh                 # free RAM/disk, taken ports, state
mkdir -p /opt/apps/<app>/production && cd /opt/apps/<app>/production
cp /opt/apps/_fondasi/server/templates/app.compose.yaml compose.yaml   # edit image, port, healthcheck
echo "8199 <app>-production <hostname>" >> /opt/apps/PORTS             # a port nothing else uses
docker compose -p <app>-production --env-file stack.env up -d --wait
curl -sI http://127.0.0.1:8199/                                         # then the tunnel route in the dashboard
sudo bash /opt/apps/_fondasi/server/check.sh                            # the app now shows "answers"
```

Memory: each MySQL/PostgreSQL takes about 300–400 MB; check free RAM before adding a stack.
