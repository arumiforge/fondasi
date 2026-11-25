# Server playbook

One flow for every VPS, from "I just got SSH access" to "the apps answer" (F-002). Every command is
idempotent, so the flow can restart at any point. App-specific steps live in each app's own docs
(SPMB: `docs/deployment.md` in `arumiforge/spmb`); what every app must follow is in
[app-contract.md](app-contract.md).

## Always start here: the check

```bash
sudo bash check.sh                                # new server: upload server/check.sh (and setup.sh)
sudo bash /opt/apps/_fondasi/server/check.sh      # once Fondasi is cloned on the server
```

`check.sh` changes nothing. It reads the host (OS, RAM, disk, pending reboot), Docker (source, engine,
Compose, Buildx, `daemon.json`, containers, ports published publicly or missing from `/opt/apps/PORTS`),
what `setup.sh` did (marker `/opt/apps/.server-setup`), firewall and SSH, the tunnel and Cockpit, every app
in `/opt/apps/PORTS` (local answer and, with a hostname column, the public URL) and each app's own
`check-app` adapter. It ends with **State**, **Next** and **Needs attention**: paste that block into a chat and the
agent knows where the server is.

## States

| State | Meaning | Next |
| --- | --- | --- |
| S0 | Fresh: no Docker, nothing public except SSH | `sudo DOMAIN=<domain> ADMIN_USER=<name> bash setup.sh` |
| S0b | Already in use: Docker and/or other public services | the same, with `ALLOW_PORTS="<ports check.sh lists>"` for services that must stay reachable |
| S0x | Docker from snap (blocker) | "Docker from snap" below |
| S1 | Set up, tunnel not connected | Cloudflare: create the tunnel, `cloudflared service install <token>` (steps 2–4) |
| S2 | Tunnel up, no app yet | each app per [app-contract.md](app-contract.md), then the app's own setup docs |
| S3 | An app needs attention: a port in `PORTS` does not answer, its hostname fails through the tunnel, or its `check-app` adapter reports a problem | the `Next` lines (they come from the adapters) |
| S9 | Every app answers | everyday work per each app's docs |

## First server, step by step

1. **`setup.sh`** (upload with SFTP; `sed -i 's/\r$//' setup.sh` if edited on Windows):
   `sudo DOMAIN=<domain> ADMIN_USER=<name> bash setup.sh`. Installs or keeps Docker, cloudflared, Cockpit on
   `127.0.0.1:9090`, unattended security updates, swap, journald limits, ufw, `/opt/apps` with `PORTS`.
2. **Tunnel** (F-004): Cloudflare Zero Trust → Networks → Tunnels → *Create* (cloudflared) → run the shown
   `cloudflared service install <token>`. Public hostnames: `ssh.<domain>` → `ssh://127.0.0.1:<ssh port>`,
   `konsol.<domain>` → `http://127.0.0.1:9090`.
3. **Access**: one Access application for `ssh.`, `konsol.` and every staging hostname (allow the developers'
   emails). Production sites stay public. SSL/TLS "Full", "Always Use HTTPS".
4. **Key-only SSH**: add your public key for root and the admin user, sign in with it while the password
   session stays open, run `setup.sh` again from the key session: password login goes off. The direct SSH
   port stays open on purpose (last way in when the tunnel is down). Never install fail2ban on a NAT VPS.
5. **Fondasi on the server**: a read-only deploy key per repository with an SSH alias:

   ```bash
   ssh-keygen -t ed25519 -f /root/.ssh/fondasi_deploy -N "" -C "$(hostname) fondasi (read-only)"
   printf 'Host github-fondasi\n  HostName github.com\n  User git\n  IdentityFile /root/.ssh/fondasi_deploy\n  IdentitiesOnly yes\n' >> /root/.ssh/config
   cat /root/.ssh/fondasi_deploy.pub   # GitHub → arumiforge/fondasi → Settings → Deploy keys (read-only)
   git clone git@github-fondasi:arumiforge/fondasi.git /opt/apps/_fondasi
   ```

   Update later with `git -C /opt/apps/_fondasi pull`.
6. **Apps**: [app-contract.md](app-contract.md).

## Fresh server vs a server already in use

| Item | Fresh (S0) | Already in use (S0b) |
| --- | --- | --- |
| Docker packages | Installs `docker-ce` + Compose + Buildx | Keeps `docker-ce` (adds plugins) or Ubuntu's `docker.io` (adds `docker-compose-v2`, `docker-buildx`); never replaces an engine |
| `daemon.json` | Writes `live-restore` + log limits | Merges them in (backup kept); other keys and a deliberately chosen log driver stay; invalid JSON is left alone |
| Docker restart | Yes (nothing runs yet) | Never while containers run: reload only; restart later in a quiet hour |
| Firewall | Deny incoming, SSH open | ufw stays off while a public service is not in `ALLOW_PORTS`; `FIREWALL=on` closes them, `FIREWALL=off` leaves ufw alone |
| Containers on `0.0.0.0` | — | Warned: Docker bypasses ufw; move them to `127.0.0.1` + tunnel |
| Lock-out guards | SSH port always open, password login off only after a proven key, sshd reloaded never restarted, network config untouched | same |

### Docker from snap

Two engines fight over the socket and iptables, so neither script removes snap Docker. In a quiet hour:
list containers and volumes (`snap run docker ps -a`, `docker volume ls`), back up their data, stop them,
`sudo snap remove --purge docker`, run `setup.sh`, start the stacks again and restore their data.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| A site gives 502 / 1033 | `check.sh` (does the port answer locally?), then the app's logs; tunnel route port matches `PORTS` |
| SSH through the tunnel down | Cockpit at `https://konsol.<domain>` → Terminal |
| Tunnel down | Direct SSH with your key on the provider's SSH port; `systemctl status cloudflared` |
| "Could not get lock … unattended-upgr" | A fresh server updates itself first; `setup.sh` waits; never kill it |
| Disk full | `docker system df`, `docker image prune`, old backups under `/opt/apps/<app>/<env>/backups/` |
| Reboot pending | Reboot in a quiet hour; containers come back (`restart: unless-stopped`) |
