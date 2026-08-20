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

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass

HOTSPOT_CONNECTION = "ktog-setup"
WIFI_TIMEOUT = 45  # nmcli blocks until the association succeeds or gives up

_DEPLOY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deploy"
)
HOTSPOT_SCRIPT = os.path.join(_DEPLOY_DIR, "ktog-hotspot.sh")
HOTSPOT_DEFAULTS = "/etc/default/ktog-hotspot"
HOTSPOT_LOG = "/var/log/ktog-hotspot.log"
ALWAYS_RE = re.compile(r"^\s*KTOG_HOTSPOT_ALWAYS\s*=")


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


def hotspot_always() -> bool:
    """Is the access point configured to come up at every boot?"""
    try:
        with open(HOTSPOT_DEFAULTS) as handle:
            for line in handle:
                if ALWAYS_RE.match(line):
                    _, _, value = line.partition("=")
                    return value.strip().strip('"').strip("'") == "1"
    except OSError:
        pass
    return False


def set_hotspot_always(enabled: bool) -> None:
    """Rewrite only the KTOG_HOTSPOT_ALWAYS line, atomically."""
    try:
        with open(HOTSPOT_DEFAULTS) as handle:
            lines = handle.readlines()
    except OSError:
        lines = []

    new_line = f"KTOG_HOTSPOT_ALWAYS={1 if enabled else 0}\n"
    for i, line in enumerate(lines):
        if ALWAYS_RE.match(line):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)

    directory = os.path.dirname(HOTSPOT_DEFAULTS) or "."
    fd, tmp = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.writelines(lines)
        os.chmod(tmp, 0o644)
        os.replace(tmp, HOTSPOT_DEFAULTS)
    except BaseException:
        os.unlink(tmp)
        raise


def switch_hotspot(on: bool) -> None:
    """Raise or tear down the access point, without waiting for the result.

    Both directions cut the network the browser is talking over (the Wi-Fi
    client connection, or the access point itself), so the HTTP answer must be
    sent before the switch happens: the script runs detached and its output
    goes to HOTSPOT_LOG for the page to show afterwards.
    """
    log = open(HOTSPOT_LOG, "w")
    with log:
        subprocess.Popen(
            ["/bin/bash", HOTSPOT_SCRIPT, "--now" if on else "--off"],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )


def hotspot_log(lines: int) -> list[str]:
    try:
        with open(HOTSPOT_LOG) as handle:
            return handle.read().splitlines()[-lines:]
    except OSError:  # never switched from the page
        return []
