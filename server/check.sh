#!/usr/bin/env bash
# Server check: where is this server on the way to running apps, and what is the next command?
# Read-only: it changes nothing, so it is safe on any server, fresh or busy (Fondasi F-002).
# docs/server-playbook.md in arumiforge/fondasi explains every state and step.
#
#   sudo bash check.sh                       # before setup.sh: upload this file next to it
#   sudo bash /opt/apps/_fondasi/server/check.sh   # once Fondasi is cloned on the server
#   sudo DOMAIN=example.sch.id bash check.sh # fills the domain into the printed commands
#
# Apps are read from /opt/apps/PORTS ("<port> <app>-<env> [public hostname]"). An app can add its own
# read-only checks as /opt/apps/<app>/check-app (docs/app-contract.md, "App check adapter").
#
# Variables (optional): DOMAIN (production domain, for the printed commands),
# APPS_ROOT (default /opt/apps; SPMB_ROOT still accepted), OFFLINE=1 (skip the network checks: repository, public URLs).
#
# Output: one line per check ([ok] fine, [--] not done yet, [!!] needs attention), then the
# state of the server (S0…S9) and the next command(s). Exit code 0, or 1 when a blocker was found.
set -uo pipefail

APPS_ROOT="${APPS_ROOT:-${SPMB_ROOT:-/opt/apps}}"
DOMAIN="${DOMAIN:-}"
OFFLINE="${OFFLINE:-0}"
MARKER="$APPS_ROOT/.server-setup"

ok()   { printf '  [ok] %s\n' "$*"; }
todo() { printf '  [--] %s\n' "$*"; }
bad()  { printf '  [!!] %s\n' "$*"; WARNINGS+=("$*"); }
info() { printf '       %s\n' "$*"; }
head_() { printf '\n== %s\n' "$*"; }
WARNINGS=()
BLOCKER=0

ROOT=1
[ "$(id -u)" -eq 0 ] || ROOT=0

pkg_installed() { dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q 'ok installed'; }
have() { command -v "$1" >/dev/null 2>&1; }

# "<port> <process>" for every TCP listener not bound to loopback, one line per port.
public_listeners() {
    have ss || return 0
    ss -ltnpH 2>/dev/null | awk '{
        addr = $4; port = addr; sub(/.*:/, "", port)
        host = addr; sub(/:[^:]*$/, "", host)
        if (host ~ /^127\./ || host == "[::1]" || host ~ /^\[::ffff:127\./) next
        proc = "?"
        if (match($0, /users:\(\("[^"]+"/)) proc = substr($0, RSTART + 9, RLENGTH - 10)
        print port, proc
    }' | sort -u -k1,1n
}

# Ports sshd listens on (ssh.socket on Ubuntu 24.04, otherwise sshd's own config).
ssh_ports() {
    if systemctl is-active --quiet ssh.socket 2>/dev/null; then
        systemctl show -p Listen --value ssh.socket | grep -oE ':[0-9]+ ' | tr -d ': '
    else
        sshd -T 2>/dev/null | awk '$1 == "port" {print $2}'
    fi | sort -un | tr '\n' ' '
}

# Containers that publish a port on a non-loopback address: "<name> <host:port>".
docker_public_ports() {
    docker ps --format '{{.Names}}|{{.Ports}}' 2>/dev/null | while IFS='|' read -r name ports; do
        tr ',' '\n' <<< "$ports" | sed 's/^ *//' | grep -- '->' | while read -r p; do
            host="${p%%->*}"
            case "$host" in 127.*|'[::1]'*|'::1'*) ;; *) printf '%s %s\n' "$name" "$host" ;; esac
        done
    done | sort -u
}

http_code() {
    curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$@" 2>/dev/null || true
}

# ------------------------------------------------------------------------------------------
head_ "Host"
# shellcheck disable=SC1091
. /etc/os-release 2>/dev/null || true
if [ "${ID:-}" = ubuntu ] && [ "${VERSION_ID:-}" = 24.04 ]; then
    ok "${PRETTY_NAME:-Ubuntu 24.04}"
else
    bad "${PRETTY_NAME:-unknown OS}: the scripts are written for Ubuntu Server 24.04."
fi
[ "$ROOT" = 1 ] || bad "Not running as root: some checks are limited (run: sudo bash check.sh)."
virt="$(systemd-detect-virt 2>/dev/null || true)"
case "$virt" in
    lxc|lxc-libvirt|openvz) bad "This server is a '$virt' container: Docker, swap and the firewall may not work." ;;
    *) ok "Virtualisation: ${virt:-unknown}" ;;
esac
mem_total="$(awk '/^MemTotal/ {printf "%d", $2 / 1024}' /proc/meminfo)"
mem_avail="$(awk '/^MemAvailable/ {printf "%d", $2 / 1024}' /proc/meminfo)"
swap_total="$(awk '/^SwapTotal/ {printf "%d", $2 / 1024}' /proc/meminfo)"
if [ "${mem_total:-0}" -lt 1800 ]; then
    bad "RAM ${mem_total} MB (${mem_avail} MB free): staging + production need about 2 GB."
else
    ok "RAM ${mem_total} MB (${mem_avail} MB free), swap ${swap_total} MB"
fi
disk_dir="$APPS_ROOT"; [ -d "$disk_dir" ] || disk_dir=/
disk_free_gb="$(df -Pk "$disk_dir" | awk 'NR == 2 {printf "%d", $4 / 1048576}')"
if [ "${disk_free_gb:-0}" -lt 8 ]; then
    bad "Disk: only ${disk_free_gb} GB free on $disk_dir (images, database and backups need room)."
else
    ok "Disk: ${disk_free_gb} GB free on $disk_dir"
fi
[ ! -f /var/run/reboot-required ] || bad "A reboot is pending (/var/run/reboot-required): reboot in a quiet hour."

# ------------------------------------------------------------------------------------------
head_ "Docker"
DOCKER_SRC=none
if have snap && snap list docker >/dev/null 2>&1; then DOCKER_SRC=snap
elif pkg_installed docker-ce; then DOCKER_SRC=docker-ce
elif pkg_installed docker.io; then DOCKER_SRC=docker.io
elif have docker; then DOCKER_SRC=other
fi
DOCKER_UP=0
CONTAINERS=0
PROJECTS=""
case "$DOCKER_SRC" in
    none)
        todo "Docker is not installed (setup.sh installs it)." ;;
    snap)
        bad "Docker comes from snap. the apps need Docker from apt: see docs/server-playbook.md, 'Docker from snap'."
        BLOCKER=1 ;;
    *)
        case "$DOCKER_SRC" in
            docker-ce) ok "Docker from Docker's own packages (docker-ce)" ;;
            docker.io) ok "Docker from Ubuntu's packages (docker.io); setup.sh keeps it and adds what is missing" ;;
            other) bad "A 'docker' command exists but not from apt (Podman? a manual install?): check by hand." ;;
        esac
        if docker info >/dev/null 2>&1; then
            DOCKER_UP=1
            ok "Engine $(docker version -f '{{.Server.Version}}' 2>/dev/null) is running"
        else
            bad "The Docker engine does not answer (systemctl status docker)."
        fi
        if docker compose version >/dev/null 2>&1; then
            ok "Compose $(docker compose version --short 2>/dev/null)"
        else
            todo "Compose v2 plugin missing (setup.sh installs it)."
        fi
        if docker buildx version >/dev/null 2>&1; then
            ok "Buildx (BuildKit) available"
        else
            todo "Buildx missing (setup.sh installs it; app deploys build with BuildKit)."
        fi
        if [ -f /etc/docker/daemon.json ] && have jq; then
            if ! jq -e . /etc/docker/daemon.json >/dev/null 2>&1; then
                bad "/etc/docker/daemon.json is not valid JSON; setup.sh will leave it alone."
            elif [ "$(jq -r '."live-restore" // false' /etc/docker/daemon.json)" = true ]; then
                ok "daemon.json: live-restore on (containers survive a Docker restart)"
            else
                todo "daemon.json: live-restore off (setup.sh adds it without restarting running containers)."
            fi
        else
            todo "No /etc/docker/daemon.json yet (setup.sh writes live-restore and log limits)."
        fi
        if [ "$DOCKER_UP" = 1 ]; then
            CONTAINERS="$(docker ps -q | wc -l)"
            PROJECTS="$(docker ps -a --format '{{.Label "com.docker.compose.project"}}' | sort -u | grep -v '^$' | tr '\n' ' ')"
            info "Containers running: $CONTAINERS; compose projects: ${PROJECTS:-none}"
            while read -r name hostport; do
                [ -n "$name" ] || continue
                bad "Container $name publishes $hostport on a public address. Docker bypasses ufw, so this port is open to the internet; publish on 127.0.0.1 and use the tunnel instead."
            done < <(docker_public_ports)
        fi ;;
esac

# ------------------------------------------------------------------------------------------
head_ "Server setup (setup.sh), firewall, SSH"
SETUP_DONE=0
if [ -f "$MARKER" ]; then
    SETUP_DONE=1
    ok "setup.sh has run ($(sed -n 's/^last_run=//p' "$MARKER")); server name: $(sed -n 's/^server=//p' "$MARKER" | grep . || hostname -s)"
    [ -n "$DOMAIN" ] || DOMAIN="$(sed -n 's/^domain=//p' "$MARKER")"
elif [ -f /etc/apt/apt.conf.d/52spmb-unattended-upgrades ]; then   # file name kept from the first servers
    SETUP_DONE=1
    ok "setup.sh has run (an earlier version; running it again adds the marker file)"
else
    todo "setup.sh has not run on this server."
fi
SSH_PORTS="$(ssh_ports)"; SSH_PORTS="${SSH_PORTS% }"
info "sshd listens on: ${SSH_PORTS:-unknown}"

OTHER_PUBLIC=""
while read -r port proc; do
    [ -n "$port" ] || continue
    case " $SSH_PORTS " in *" $port "*) continue ;; esac
    case "$proc" in sshd|systemd) continue ;; docker-proxy) continue ;; esac
    OTHER_PUBLIC="${OTHER_PUBLIC:+$OTHER_PUBLIC }$port"
    info "Also listening publicly: port $port ($proc)"
done < <(public_listeners)

if have ufw && ufw status 2>/dev/null | grep -q '^Status: active'; then
    ok "Firewall (ufw) active"
    for p in $SSH_PORTS; do
        ufw status 2>/dev/null | grep -qE "^$p(/tcp)?[[:space:]]+ALLOW" \
            || bad "ufw is active but SSH port $p has no ALLOW rule: check before closing this session."
    done
elif [ "$ROOT" = 0 ]; then
    info "Firewall state needs root to read."
else
    todo "Firewall (ufw) not active yet (setup.sh enables it, keeping SSH open)."
fi

if [ "$ROOT" = 1 ] && have sshd; then
    if [ "$(sshd -T 2>/dev/null | awk '$1 == "passwordauthentication" {print $2}')" = no ]; then
        ok "SSH: password login off (key-only)"
    else
        todo "SSH: password login still on (docs/server-playbook.md: add a key, sign in with it, run setup.sh again)."
    fi
fi

# ------------------------------------------------------------------------------------------
head_ "Admin access (Cloudflare Tunnel, Cockpit)"
TUNNEL=0
if have cloudflared; then
    if systemctl is-active --quiet cloudflared 2>/dev/null; then
        TUNNEL=1
        ok "cloudflared runs as a service (tunnel connected)"
    else
        todo "cloudflared installed, tunnel not connected yet (cloudflared service install <token>)."
    fi
else
    todo "cloudflared not installed (setup.sh installs it)."
fi
if have ss && ss -ltnH 'sport = :9090' 2>/dev/null | grep -q '127.0.0.1:9090'; then
    ok "Cockpit on 127.0.0.1:9090"
elif systemctl is-enabled --quiet cockpit.socket 2>/dev/null; then
    ok "Cockpit socket enabled"
else
    todo "Cockpit not set up (setup.sh)."
fi

# ------------------------------------------------------------------------------------------
APPS_COUNT=0
APPS_BAD=0
head_ "Apps on this server ($APPS_ROOT/PORTS)"
if [ -f "$APPS_ROOT/PORTS" ]; then
    while read -r port name host _; do
        case "$port" in ''|'#'*) continue ;; esac
        APPS_COUNT=$((APPS_COUNT + 1))
        if [ "$(http_code "http://127.0.0.1:$port/")" = 000 ]; then
            bad "$port $name — nothing answers on 127.0.0.1:$port"
            APPS_BAD=$((APPS_BAD + 1))
            continue
        fi
        if [ -z "${host:-}" ]; then
            info "$port $name — answers (no public hostname recorded: add it as a third column)"
        elif [ "$OFFLINE" = 1 ] || [ "$TUNNEL" = 0 ]; then
            info "$port $name — answers ($host)"
        else
            pub="$(http_code "https://$host/")"
            case "$pub" in
                2??|3??|401|403) ok "$port $name — answers, https://$host/ gives $pub" ;;
                *) bad "$port $name answers locally but https://$host/ gives ${pub:-nothing}: check the tunnel route $host -> http://127.0.0.1:$port"
                   APPS_BAD=$((APPS_BAD + 1)) ;;
            esac
        fi
    done < "$APPS_ROOT/PORTS"
else
    todo "No port list yet (setup.sh creates $APPS_ROOT/PORTS)."
fi
# Ports published by containers but missing from the list: the next app could pick the same port.
if [ "$DOCKER_UP" = 1 ]; then
    while IFS='|' read -r project name ports; do
        tr ',' '\n' <<< "$ports" | sed 's/^ *//' | grep -- '->' | while read -r p; do
            hostport="${p%%->*}"; port="${hostport##*:}"
            awk -v p="$port" '$1 == p {found = 1} END {exit !found}' "$APPS_ROOT/PORTS" 2>/dev/null && continue
            printf '%s %s\n' "$port" "${project:-$name}"
        done
    done < <(docker ps --format '{{.Label "com.docker.compose.project"}}|{{.Names}}|{{.Ports}}' 2>/dev/null) \
        | sort -u -k1,1n | while read -r port owner; do
            printf '  [!!] Port %s (%s) is used but not in %s: echo "%s %s" >> %s\n' \
                "$port" "$owner" "$APPS_ROOT/PORTS" "$port" "$owner" "$APPS_ROOT/PORTS"
        done
    unlisted_count="$(docker ps --format '{{.Ports}}' 2>/dev/null | tr ',' '\n' | grep -- '->' | sed 's/->.*//; s/.*://' | sort -u \
        | while read -r port; do awk -v p="$port" '$1 == p {f = 1} END {exit !f}' "$APPS_ROOT/PORTS" 2>/dev/null || echo "$port"; done | wc -l)"
    [ "$unlisted_count" -eq 0 ] || WARNINGS+=("$unlisted_count published port(s) are not in $APPS_ROOT/PORTS (lines above): add them so no two apps take the same port.")
fi

# ------------------------------------------------------------------------------------------
# App adapters (docs/app-contract.md, "App check adapter"): /opt/apps/<app>/check-app, provided by the app,
# read-only. Its "[ok]/[--]/[!!]" lines are shown here; "NEXT: …" lines become next steps; exit 0 = fine.
ADAPTER_NEXT=()
ADAPTERS_BAD=""
for adapter in "$APPS_ROOT"/*/check-app; do
    [ -f "$adapter" ] || continue
    app="$(basename "$(dirname "$adapter")")"
    head_ "App: $app"
    out="$(APPS_ROOT="$APPS_ROOT" OFFLINE="$OFFLINE" TUNNEL="$TUNNEL" DOCKER_UP="$DOCKER_UP" \
        timeout 120 bash "$adapter" 2>&1)"
    rc=$?
    while IFS= read -r line; do
        case "$line" in
            'NEXT: '*) ADAPTER_NEXT+=("$app: ${line#NEXT: }") ;;
            *'[!!] '*) printf '%s\n' "$line"; WARNINGS+=("$app: ${line#*\[!!\] }") ;;
            *) printf '%s\n' "$line" ;;
        esac
    done <<< "$out"
    [ "$rc" = 0 ] || ADAPTERS_BAD="${ADAPTERS_BAD:+$ADAPTERS_BAD }$app"
done

# ------------------------------------------------------------------------------------------
# State: the first step that is not done yet decides what comes next.
D="${DOMAIN:-<domain>}"
STATE="" ; NEXT=()
if [ "$DOCKER_SRC" = snap ]; then
    STATE="S0x  Docker from snap (blocker)"
    NEXT=("Move or stop the snap containers, then: snap remove docker   (docs/server-playbook.md, 'Docker from snap')"
          "Then run this check again.")
elif [ "$SETUP_DONE" = 0 ]; then
    allow=""; [ -z "$OTHER_PUBLIC" ] || allow=" ALLOW_PORTS=\"$OTHER_PUBLIC\""
    if [ "$DOCKER_SRC" = none ] && [ -z "$OTHER_PUBLIC" ]; then
        STATE="S0   Fresh server"
    else
        STATE="S0b  Server already in use (Docker: $DOCKER_SRC, $CONTAINERS containers, other public ports: ${OTHER_PUBLIC:-none})"
        NEXT+=("setup.sh keeps running containers up (no Docker restart while containers run) and keeps existing Docker packages.")
        [ -z "$OTHER_PUBLIC" ] || NEXT+=("Ports $OTHER_PUBLIC serve something today: ALLOW_PORTS keeps them open; leave a port out to close it.")
    fi
    NEXT+=("sudo DOMAIN=$D ADMIN_USER=<name>$allow bash setup.sh")
elif [ "$TUNNEL" = 0 ]; then
    STATE="S1   Base ready, tunnel not connected"
    NEXT=("Cloudflare Zero Trust → Networks → Tunnels → Create → run: cloudflared service install <token>"
          "Routes: ssh.$D, konsol.$D (docs/server-playbook.md, steps 2–4)")
elif [ "$APPS_COUNT" = 0 ] && [ -z "$(ls "$APPS_ROOT"/*/check-app 2>/dev/null)" ]; then
    STATE="S2   Server ready for apps"
    NEXT=("Add an app: docs/app-contract.md (folder /opt/apps/<app>, a port line in PORTS, 127.0.0.1 only,"
          "a tunnel route in the Cloudflare dashboard, optionally a check-app adapter); then its own setup docs.")
elif [ "$APPS_BAD" != 0 ] || [ -n "$ADAPTERS_BAD" ]; then
    STATE="S3   Apps need attention (${ADAPTERS_BAD:-ports that do not answer})"
    NEXT=("${ADAPTER_NEXT[@]+"${ADAPTER_NEXT[@]}"}")
    [ "$APPS_BAD" = 0 ] || NEXT+=("Ports in PORTS that do not answer: start the stack or remove its line (see the Apps section).")
else
    STATE="S9   Live: every app answers"
    NEXT=("Everyday work follows each app's own docs.")
    NEXT+=("${ADAPTER_NEXT[@]+"${ADAPTER_NEXT[@]}"}")
fi

head_ "Result"
printf '  State: %s\n' "$STATE"
printf '  Next:\n'
for n in "${NEXT[@]}"; do printf '    %s\n' "$n"; done
if [ "${#WARNINGS[@]}" -gt 0 ]; then
    printf '  Needs attention:\n'
    for w in "${WARNINGS[@]}"; do printf '    - %s\n' "$w"; done
fi
exit "$BLOCKER"
