#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
#
# Fallback access point: if the Pi has no Wi-Fi connection shortly after boot,
# it becomes an access point so the configuration page stays reachable from a
# phone. That is the only way to enter Wi-Fi credentials on a headless Pi with
# no Ethernet.
#
# Started by ktog-hotspot.service. Exits without doing anything when Wi-Fi is
# already up, so a configured Pi never advertises the setup network.
set -uo pipefail

SSID="${KTOG_HOTSPOT_SSID:-KeiserToGarmin}"
PASSWORD="${KTOG_HOTSPOT_PASSWORD:-keiser2garmin}"
CONNECTION="ktog-setup"
WAIT_SECONDS="${KTOG_HOTSPOT_WAIT:-45}"

wifi_connected() {
    nmcli -t -f TYPE,STATE device 2>/dev/null | grep -q '^wifi:connected$'
}

wifi_device() {
    nmcli -t -f DEVICE,TYPE device 2>/dev/null \
        | awk -F: '$2 == "wifi" { print $1; exit }'
}

if ! command -v nmcli >/dev/null; then
    echo "NetworkManager (nmcli) not found, nothing to do." >&2
    exit 0
fi

# NetworkManager needs time to associate with a known network after boot.
for _ in $(seq "$WAIT_SECONDS"); do
    if wifi_connected; then
        echo "Wi-Fi already connected, no hotspot needed."
        exit 0
    fi
    sleep 1
done

IFNAME="$(wifi_device)"
if [[ -z "$IFNAME" ]]; then
    echo "No Wi-Fi device, cannot start the setup hotspot." >&2
    exit 0
fi

echo "No Wi-Fi after ${WAIT_SECONDS}s, starting setup hotspot '$SSID' on $IFNAME."
# Drop a hotspot profile left over from a previous boot: its stored channel or
# band may no longer be valid, and nmcli would reuse it as-is.
nmcli connection delete "$CONNECTION" >/dev/null 2>&1
nmcli device wifi hotspot ifname "$IFNAME" con-name "$CONNECTION" \
    ssid "$SSID" password "$PASSWORD"

# Never auto-start on a later boot: the service decides each time, otherwise a
# configured Pi could come up as an access point instead of joining the house
# network.
nmcli connection modify "$CONNECTION" connection.autoconnect no

echo "Connect to '$SSID' (password: $PASSWORD) and open http://10.42.0.1:8080/"
