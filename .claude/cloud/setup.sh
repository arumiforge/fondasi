#!/usr/bin/env bash
# Cloud environment setup for Fondasi sessions (docs/cloud-environment.md). Runs as root from the folder
# that holds the checkouts. Idempotent; never fails the session start for an optional tool.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive

need=()
for tool in shellcheck jq; do command -v "$tool" >/dev/null || need+=("$tool"); done
if [ "${#need[@]}" -gt 0 ]; then
    apt-get update -q >/dev/null 2>&1 || true
    apt-get install -y -q "${need[@]}" >/dev/null 2>&1 || echo "setup: could not install ${need[*]} (optional)"
fi
command -v node >/dev/null || echo "setup: node is missing; converters in tools/converters need Node.js 20+"

for repo in fondasi server; do
    if [ -d "$repo/.git" ]; then
        git -C "$repo" config user.name "${ARUMI_GIT_NAME:-Arumi Studios}"
        git -C "$repo" config user.email "${ARUMI_GIT_EMAIL:-arumiforge@gmail.com}"
        git -C "$repo" config core.hooksPath .githooks
        (cd "$repo" && tools/data-check >/dev/null 2>&1 && echo "setup: $repo data sets verified") || echo "setup: tools/data-check reported a problem in $repo"
    fi
done
exit 0
