# Servers (more than one VPS) (F-008)

Every VPS follows the same [server playbook](server-playbook.md) and [app contract](app-contract.md); this page
is the list of servers and the rules that keep several of them apart.

## Inventory

No IP addresses, ports, passwords, keys or tokens here: they live in the provider panel and the password manager.

| Server | Provider / location | Role | Tunnel | Admin hostnames | Apps (env → hostname) |
| --- | --- | --- | --- | --- | --- |
| `spmb-prod` | NAT VPS, Indonesia | SPMB first client + other apps | one tunnel on the developer's Cloudflare account | `konsol.spmbsmpnualmarufkudus.web.id`, `ssh.spmbsmpnualmarufkudus.web.id` | `spmb-staging`, `spmb-production`, `milklife-staging` |

Add a row when a server is set up; update the apps column when an app moves. `check.sh` prints the server name
from `/opt/apps/.server-setup` (`SERVER_NAME=<label>` when running `setup.sh`).

## Rules for several servers

| Rule | Why |
| --- | --- |
| Each VPS gets a short label (`spmb-prod`, `edu-2`, `atletik-1`), used as `SERVER_NAME`, in this table and in the tunnel's name | One name for the same machine everywhere |
| One tunnel per VPS (F-004); never share a tunnel token between servers | A tunnel's connectors are treated as one server; sharing would send traffic to the wrong machine |
| Admin hostnames per server: `konsol-<label>.<admin domain>` and `ssh-<label>.<admin domain>` (one level, so Cloudflare's free certificate covers them); existing servers keep their names | Cockpit and SSH of different servers never collide |
| One Access application can cover the admin hostnames of every server | One sign-in policy |
| Ports and `/opt/apps/PORTS` are per server; the same app may use different ports on different servers | Ports are local to a machine |
| A deploy key per repository **per server** (`<server> <repo> (read-only)` as its title) | Revoke one server without touching the others |
| Location matters for personal data: public-sector clients need a VPS in Indonesia ([storage.md](storage.md)) | PP 71/2019 |
| Each server has its own off-site backup prefix (`<label>/<app>/<env>`) | Restores never mix servers |

## Moving an app to another server

1. New server: playbook S0 → S2 (`check.sh`, `setup.sh SERVER_NAME=<label>`, its own tunnel, Fondasi checkout).
2. Old server: backup of each environment (database + files + env file; SPMB: `spmb backup <env>`); copy the
   archives to the new server (`scp`/`rsync` over SSH, never through a public URL).
3. New server: set the app up per the app contract (SPMB: `spmb init` + `spmb deploy <env> <commit from backup.info>`),
   restore the backup (SPMB: `spmb restore`), check it locally with `check.sh`.
4. Cloudflare: move the app's public hostname from the old tunnel to the new one (delete the route on the old
   tunnel, add it on the new one → `http://127.0.0.1:<new port>`). The switch is immediate; keep the old stack
   stopped (not deleted) for a few days.
5. Update this table and the `PORTS` files on both servers; remove the old stack and its backups when sure.
