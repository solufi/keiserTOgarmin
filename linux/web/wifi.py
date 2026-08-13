# SPDX-License-Identifier: GPL-3.0-only
"""Wi-Fi status, scanning and joining through NetworkManager.

Raspberry Pi OS Bookworm manages Wi-Fi with NetworkManager, so `nmcli` is the
supported way in and it keeps the credentials for us (no wpa_supplicant.conf
editing, no reboot). Everything here shells out to nmcli in terse mode, whose
output is field-separated and stable across versions:

    nmcli -t -f SSID,SIGNAL,SECURITY device wifi list

The hotspot connection created by `deploy/ktog-hotspot.sh` is skipped from the
scan results: joining it from itself makes no sense and it is the network the
user is most likely browsing from.
"""

import re
import subprocess
from dataclasses import dataclass

HOTSPOT_CONNECTION = "ktog-setup"
WIFI_TIMEOUT = 45  # nmcli blocks until the association succeeds or gives up


@dataclass
class Network:
    ssid: str
    signal: int
    secured: bool
    active: bool


def _nmcli(*args: str, timeout: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["nmcli", *args], capture_output=True, text=True, timeout=timeout
    )


def available() -> bool:
    """False on a system without NetworkManager, so the UI can hide the panel."""
    try:
        return _nmcli("--version", timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _split_terse(line: str) -> list[str]:
    """nmcli escapes the field separator as '\\:' inside values (e.g. in a BSSID)."""
    return [field.replace("\\:", ":") for field in re.split(r"(?<!\\):", line)]


def current() -> str | None:
    """SSID of the connected network, or None (also None while running the hotspot)."""
    result = _nmcli("-t", "-f", "ACTIVE,SSID", "device", "wifi")
    for line in result.stdout.splitlines():
        fields = _split_terse(line)
        if len(fields) >= 2 and fields[0] == "yes":
            return fields[1] or None
    return None


def hotspot_active() -> bool:
    result = _nmcli("-t", "-f", "NAME", "connection", "show", "--active")
    return HOTSPOT_CONNECTION in result.stdout.split()


def scan(rescan: bool = True) -> list[Network]:
    """Strongest first, one entry per SSID; raises RuntimeError if nmcli fails."""
    args = ["-t", "-f", "ACTIVE,SSID,SIGNAL,SECURITY", "device", "wifi", "list"]
    if rescan and not hotspot_active():
        # Rescanning while acting as an access point drops the clients that are
        # browsing this very page, so only refresh when we are not the AP.
        args.append("--rescan")
        args.append("yes")
    result = _nmcli(*args, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "nmcli failed")

    best: dict[str, Network] = {}
    for line in result.stdout.splitlines():
        fields = _split_terse(line)
        if len(fields) < 4:
            continue
        active, ssid, signal, security = fields[0], fields[1], fields[2], fields[3]
        if not ssid or ssid == HOTSPOT_CONNECTION:
            continue
        try:
            strength = int(signal)
        except ValueError:
            strength = 0
        network = Network(
            ssid=ssid,
            signal=strength,
            secured=bool(security and security != "--"),
            active=active == "yes",
        )
        known = best.get(ssid)
        if known is None or network.signal > known.signal:
            best[ssid] = network

    return sorted(best.values(), key=lambda n: n.signal, reverse=True)


def connect(ssid: str, password: str) -> None:
    """Join `ssid`, raising RuntimeError with nmcli's own message on failure.

    A stale profile for the same SSID (wrong password from a previous attempt)
    would make nmcli reuse it and fail again, so it is deleted first.
    """
    if not ssid:
        raise RuntimeError("SSID is empty")

    _nmcli("connection", "delete", ssid)
    args = ["device", "wifi", "connect", ssid]
    if password:
        args += ["password", password]
    result = _nmcli(*args, timeout=WIFI_TIMEOUT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "connection failed")

    # Survive the setup hotspot being torn down later and reboots.
    _nmcli("connection", "modify", ssid, "connection.autoconnect", "yes")


def stop_hotspot() -> None:
    _nmcli("connection", "down", HOTSPOT_CONNECTION)
