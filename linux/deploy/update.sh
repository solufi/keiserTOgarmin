#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
#
# Pull the latest code and re-run the installer, so a user with no shell can
# update from the "Update" button of the configuration page.
#
# Usage:  sudo ./linux/deploy/update.sh
#
# Started detached by the web UI: it restarts the web service itself, which
# would otherwise kill the HTTP response mid-update.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if [[ $EUID -ne 0 ]]; then
    echo "This script must run as root (sudo $0)." >&2
    exit 1
fi

echo "==> $(date '+%Y-%m-%d %H:%M:%S') updating $REPO_ROOT"
echo "==> Current revision: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"

# Untracked files are ignored on purpose: a stray note or log next to the code
# must not block the update, only edits to tracked files can conflict.
if [[ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]]; then
    echo "Local changes present, refusing to pull. Commit or discard them:" >&2
    git status --short --untracked-files=no >&2
    exit 1
fi

# git refuses to operate on a repository owned by another user, and the clone
# belongs to the login user while this script runs as root.
OWNER="$(stat -c %U .git)"
git_as_owner() {
    if command -v runuser >/dev/null; then
        runuser -u "$OWNER" -- git "$@"
    else
        su "$OWNER" -s /bin/sh -c "git $*"
    fi
}

echo "==> git pull (as $OWNER)"
if ! git_as_owner pull --ff-only; then
    echo "git pull failed (no network, or the branch diverged)." >&2
    exit 1
fi

echo "==> Revision after pull: $(git rev-parse --short HEAD)"

# The installer is idempotent and keeps /etc/default/ktog, so it is also
# the update path: it refreshes the venv and rewrites the systemd units, which
# a plain "git pull" cannot do.
echo "==> Running the installer"
if ! ./linux/deploy/install-rpi.sh; then
    echo "Installer failed, services left untouched." >&2
    exit 1
fi

echo "==> Restarting services"
systemctl restart ktog.service || true
# Last: this kills the page that started the update. The browser reconnects on
# the next refresh and this log is what it displays.
systemctl restart ktog-web.service

echo "==> Update finished"
