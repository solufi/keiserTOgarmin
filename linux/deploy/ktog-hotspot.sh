#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
#
# Access point management for the configuration page.
#
#   ktog-hotspot.sh          at boot (ktog-hotspot.service): raise the access
#                            point only when no Wi-Fi shows up, unless
#                            KTOG_HOTSPOT_ALWAYS=1 asks for it every time.
#   ktog-hotspot.sh --now    raise it immediately, disconnecting Wi-Fi first.
#   ktog-hotspot.sh --off    tear it down and let NetworkManager rejoin Wi-Fi.
#
# On a headless Pi with no Ethernet, the access point is the only way in to
# enter Wi-Fi credentials -- and at the gym it is also the normal way to reach
# the page, hence --now and the KTOG_HOTSPOT_ALWAYS switch.
set -uo pipefail

DEFAULTS_FILE="${KTOG_HOTSPOT_DEFAULTS:-/etc/default/ktog-hotspot}"
# shellcheck source=/dev/null
[[ -r "$DEFAULTS_FILE" ]] && . "$DEFAULTS_FILE"

SSID="${KTOG_HOTSPOT_SSID:-KeiserToGarmin}"
PASSWORD="${KTOG_HOTSPOT_PASSWORD:-keiser2garmin}"
ALWAYS="${KTOG_HOTSPOT_ALWAYS:-0}"
CONNECTION="ktog-setup"
WAIT_SECONDS="${KTOG_HOTSPOT_WAIT:-45}"

MODE="boot"
case "${1:-}" in
    --now) MODE="now" ;;
    --off) MODE="off" ;;
    "") ;;
    *) echo "Usage: $0 [--now|--off]" >&2; exit 2 ;;
esac

wifi_connected() {
    nmcli -t -f TYPE,STATE device 2>/dev/null | grep -q '^wifi:connected$'
}

wifi_device() {
    nmcli -t -f DEVICE,TYPE device 2>/dev/null \
        | awk -F: '$2 == "wifi" { print $1; exit }'
}

hotspot_up() {
    nmcli -t -f NAME connection show --active 2>/dev/null \
        | grep -qx "$CONNECTION"
}

if ! command -v nmcli >/dev/null; then
    echo "NetworkManager (nmcli) not found, nothing to do." >&2
    exit 0
fi

echo "==> $(date '+%Y-%m-%d %H:%M:%S') mode=$MODE always=$ALWAYS"

if [[ "$MODE" == "off" ]]; then
    nmcli connection down "$CONNECTION" >/dev/null 2>&1
    IFNAME="$(wifi_device)"
    # `device disconnect` used by --now sets a manual flag that blocks
    # autoconnect until the device is explicitly brought up again.
    [[ -n "$IFNAME" ]] && nmcli device connect "$IFNAME" >/dev/null 2>&1
    echo "Access point stopped, rejoining Wi-Fi."
    exit 0
fi

# The radio may be soft-blocked (rfkill) on a fresh image, and no Wi-Fi country
# means no access point at all: nmcli then fails with an unhelpful message.
rfkill unblock wifi >/dev/null 2>&1
nmcli radio wifi on >/dev/null 2>&1

if [[ "$MODE" == "boot" && "$ALWAYS" != "1" ]]; then
    # NetworkManager needs time to associate with a known network after boot.
    for _ in $(seq "$WAIT_SECONDS"); do
        if wifi_connected; then
            echo "Wi-Fi already connected, no hotspot needed."
            exit 0
        fi
        sleep 1
    done
    echo "No Wi-Fi after ${WAIT_SECONDS}s, starting the setup hotspot."
fi

if hotspot_up; then
    echo "Access point '$SSID' already up."
    exit 0
fi

IFNAME="$(wifi_device)"
if [[ -z "$IFNAME" ]]; then
    echo "No Wi-Fi device, cannot start the access point." >&2
    exit 1
fi

# A Wi-Fi connection on the same radio wins over the AP profile, so drop it
# first: this is what makes the button work while connected to the house
# network.
if wifi_connected; then
    echo "Disconnecting $IFNAME from Wi-Fi to free the radio."
    nmcli device disconnect "$IFNAME" >/dev/null 2>&1
fi

echo "Starting access point '$SSID' on $IFNAME."
# Drop a hotspot profile left over from a previous boot: its stored channel or
# band may no longer be valid, and nmcli would reuse it as-is.
nmcli connection delete "$CONNECTION" >/dev/null 2>&1
if ! nmcli device wifi hotspot ifname "$IFNAME" con-name "$CONNECTION" \
        ssid "$SSID" password "$PASSWORD"; then
    echo "nmcli refused to start the access point." >&2
    echo "Check the Wi-Fi country (raspi-config > Localisation) and that the" >&2
    echo "adapter supports AP mode:  iw list | grep -A5 'interface modes'" >&2
    exit 1
fi

# Never auto-start on a later boot: the service decides each time, otherwise a
# configured Pi could come up as an access point instead of joining the house
# network.
nmcli connection modify "$CONNECTION" connection.autoconnect no

echo "Connect to '$SSID' (password: $PASSWORD) and open http://10.42.0.1:8080/"
