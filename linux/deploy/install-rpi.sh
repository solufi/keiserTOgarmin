#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
#
# One-shot installer for the FreeFitness Linux bridge on a Raspberry Pi
# (or any Debian/Ubuntu based SBC). Installs system packages, builds a
# virtualenv, and registers the systemd service + ANT+ udev rule.
#
# Usage:  sudo ./linux/deploy/install-rpi.sh [--no-service] [--hostname ktog]
#
# --hostname renames the Pi so the page answers on http://<name>.local:8080/.
# Without it the current hostname is left alone.
#
# Set PYTHON=/path/to/python3.x to build the virtualenv with a specific
# interpreter instead of the system python3.
set -euo pipefail

INSTALL_SERVICE=1
NEW_HOSTNAME=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-service) INSTALL_SERVICE=0 ;;
        --hostname) NEW_HOSTNAME="${2:-}"; shift ;;
        --hostname=*) NEW_HOSTNAME="${1#*=}" ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
    shift
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINUX_DIR="$REPO_ROOT/linux"
DEPLOY_DIR="$LINUX_DIR/deploy"
VENV_DIR="$REPO_ROOT/.venv"
PYTHON="${PYTHON:-python3}"
DEFAULTS_FILE="/etc/default/freefitness"
UNIT_DIR="/etc/systemd/system"
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
# avahi-daemon answers <hostname>.local, which is how the page is reached
# without knowing the Pi's IP address.
apt-get install -y --no-install-recommends \
    bluez libusb-1.0-0 python3-venv python3-dev git avahi-daemon
systemctl enable --now avahi-daemon || true

echo "==> Creating virtualenv at $VENV_DIR"
"$PYTHON" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade -q pip
"$VENV_DIR/bin/pip" install -q -r "$REPO_ROOT/requirements.txt"

echo "==> Enabling Bluetooth"
# Raspberry Pi OS Lite leaves the controller soft-blocked and the service
# disabled, which surfaces as "No powered Bluetooth adapters found".
command -v rfkill >/dev/null && rfkill unblock bluetooth || true
systemctl enable --now bluetooth || true

if [[ -n "$NEW_HOSTNAME" ]]; then
    if [[ "$NEW_HOSTNAME" =~ ^[a-zA-Z0-9-]{1,63}$ ]]; then
        echo "==> Renaming host to $NEW_HOSTNAME"
        OLD_HOSTNAME="$(hostname)"
        hostnamectl set-hostname "$NEW_HOSTNAME"
        # /etc/hosts keeps the old name, which makes sudo slow to resolve it.
        sed -i "s/\b$OLD_HOSTNAME\b/$NEW_HOSTNAME/g" /etc/hosts
        systemctl restart avahi-daemon || true
    else
        echo "Invalid hostname '$NEW_HOSTNAME' (letters, digits and dashes only)." >&2
        exit 1
    fi
fi

echo "==> Installing ANT+ udev rule"
install -m 0644 "$DEPLOY_DIR/99-ant-usb.rules" "$UDEV_FILE"
udevadm control --reload-rules
udevadm trigger --subsystem-match=usb || true

if [[ $INSTALL_SERVICE -eq 1 ]]; then
    if [[ -f "$DEFAULTS_FILE" ]]; then
        echo "==> Keeping existing $DEFAULTS_FILE"
        # Already configured: don't greet an existing user with the wizard.
        mkdir -p /var/lib/ktog
        touch /var/lib/ktog/setup-done
    else
        echo "==> Writing $DEFAULTS_FILE"
        install -m 0644 "$DEPLOY_DIR/freefitness.default" "$DEFAULTS_FILE"
    fi

    echo "==> Installing systemd units"
    chmod 0755 "$DEPLOY_DIR/ktog-hotspot.sh"
    for template in freefitness.service freefitness-web.service ktog-hotspot.service; do
        sed -e "s|@LINUX_DIR@|$LINUX_DIR|g" \
            -e "s|@VENV_DIR@|$VENV_DIR|g" \
            -e "s|@DEPLOY_DIR@|$DEPLOY_DIR|g" \
            "$DEPLOY_DIR/$template.in" > "$UNIT_DIR/$template"
        chmod 0644 "$UNIT_DIR/$template"
    done
    systemctl daemon-reload
    systemctl enable freefitness.service
    systemctl enable --now freefitness-web.service

    # The fallback access point is pointless without NetworkManager (older Pi
    # OS images still use dhcpcd/wpa_supplicant).
    if command -v nmcli >/dev/null; then
        if [[ -f /etc/default/ktog-hotspot ]]; then
            echo "==> Keeping existing /etc/default/ktog-hotspot"
        else
            install -m 0644 "$DEPLOY_DIR/ktog-hotspot.default" \
                /etc/default/ktog-hotspot
        fi
        systemctl enable ktog-hotspot.service
    else
        echo "==> NetworkManager not found, skipping the Wi-Fi setup hotspot"
    fi
    echo
    echo "Bridge installed but not started. Configure it from a browser at"
    echo "    http://$(hostname).local:8080/   (or http://<pi-ip>:8080/)"
    if command -v nmcli >/dev/null; then
        echo
        echo "If the Pi ever boots without Wi-Fi, it raises the access point"
        echo "'KeiserToGarmin' (password keiser2garmin): join it and open"
        echo "    http://10.42.0.1:8080/"
        echo "The page can also raise it on demand, or always at boot"
        echo "(KTOG_HOTSPOT_ALWAYS in /etc/default/ktog-hotspot)."
    fi
    echo "or edit $DEFAULTS_FILE by hand, then:  sudo systemctl start freefitness"
fi

cat <<EOF

==> Done.

Quick check without a bike (simulated power, BLE output):
    cd $LINUX_DIR && sudo $VENV_DIR/bin/python main.py --mock --protocols ble

Logs once the service runs:
    journalctl -u freefitness -f
EOF
