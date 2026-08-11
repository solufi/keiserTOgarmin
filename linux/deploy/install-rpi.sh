#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
#
# One-shot installer for the FreeFitness Linux bridge on a Raspberry Pi
# (or any Debian/Ubuntu based SBC). Installs system packages, builds a
# virtualenv, and registers the systemd service + ANT+ udev rule.
#
# Usage:  sudo ./linux/deploy/install-rpi.sh [--no-service]
#
# Set PYTHON=/path/to/python3.x to build the virtualenv with a specific
# interpreter instead of the system python3.
set -euo pipefail

INSTALL_SERVICE=1
[[ "${1:-}" == "--no-service" ]] && INSTALL_SERVICE=0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINUX_DIR="$REPO_ROOT/linux"
DEPLOY_DIR="$LINUX_DIR/deploy"
VENV_DIR="$REPO_ROOT/.venv"
PYTHON="${PYTHON:-python3}"
DEFAULTS_FILE="/etc/default/freefitness"
UNIT_FILE="/etc/systemd/system/freefitness.service"
UDEV_FILE="/etc/udev/rules.d/99-ant-usb.rules"

if [[ $EUID -ne 0 ]]; then
    echo "This script must run as root (sudo $0)." >&2
    exit 1
fi

# main.py uses asyncio.TaskGroup, which landed in 3.11. Raspberry Pi OS
# Bookworm ships 3.11; Bullseye ships 3.9 and will fail at startup.
if ! "$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    echo "Python 3.11+ required, found $("$PYTHON" --version). Upgrade to Raspberry Pi OS Bookworm or newer." >&2
    exit 1
fi

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y --no-install-recommends \
    bluez libusb-1.0-0 python3-venv python3-dev

echo "==> Creating virtualenv at $VENV_DIR"
"$PYTHON" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade -q pip
"$VENV_DIR/bin/pip" install -q -r "$REPO_ROOT/requirements.txt"

echo "==> Installing ANT+ udev rule"
install -m 0644 "$DEPLOY_DIR/99-ant-usb.rules" "$UDEV_FILE"
udevadm control --reload-rules
udevadm trigger --subsystem-match=usb || true

if [[ $INSTALL_SERVICE -eq 1 ]]; then
    if [[ -f "$DEFAULTS_FILE" ]]; then
        echo "==> Keeping existing $DEFAULTS_FILE"
    else
        echo "==> Writing $DEFAULTS_FILE"
        install -m 0644 "$DEPLOY_DIR/freefitness.default" "$DEFAULTS_FILE"
    fi

    echo "==> Installing systemd unit"
    sed -e "s|@LINUX_DIR@|$LINUX_DIR|g" \
        -e "s|@VENV_DIR@|$VENV_DIR|g" \
        "$DEPLOY_DIR/freefitness.service.in" > "$UNIT_FILE"
    chmod 0644 "$UNIT_FILE"
    systemctl daemon-reload
    systemctl enable freefitness.service
    echo
    echo "Service installed but not started. Edit $DEFAULTS_FILE to set your"
    echo "bike ID and protocols, then run:  sudo systemctl start freefitness"
fi

cat <<EOF

==> Done.

Quick check without a bike (simulated power, BLE output):
    cd $LINUX_DIR && sudo $VENV_DIR/bin/python main.py --mock --protocols ble

Logs once the service runs:
    journalctl -u freefitness -f
EOF
