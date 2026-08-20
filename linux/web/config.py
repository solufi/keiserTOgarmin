# SPDX-License-Identifier: GPL-3.0-only
"""Read/write the KTOG_ARGS line of /etc/default/ktog.

The systemd unit passes that variable verbatim to main.py, so the web UI
speaks the same language as the command line: it parses the existing
arguments into a Config, and renders a Config back into arguments. Comments
in the file are preserved because only the KTOG_ARGS line is
rewritten.
"""

import os
import re
import shlex
import tempfile
from dataclasses import dataclass, field

DEFAULTS_FILE = "/etc/default/ktog"
ARGS_RE = re.compile(r"^\s*KTOG_ARGS\s*=")

# Touched when the setup wizard is finished or skipped, so a configured Pi
# stops opening it. A file rather than a line in DEFAULTS_FILE: this is state,
# not configuration, and it must not end up in KTOG_ARGS.
SETUP_FLAG = "/var/lib/ktog/setup-done"


@dataclass
class Config:
    bike_id: int = 0
    protocols: list[str] = field(default_factory=lambda: ["ble"])
    # Mirrors main.py's own defaults so a config that omits an argument is
    # displayed as what the bridge actually does.
    ble_profiles: list[str] = field(default_factory=lambda: ["cp", "csc"])
    mock: bool = False

    def to_args(self) -> str:
        args = ["--bike-id", str(self.bike_id)]
        if self.mock:
            args.append("--mock")
        args += ["--protocols", ",".join(self.protocols)]
        if "ble" in self.protocols:
            args += ["--ble-profiles", ",".join(self.ble_profiles)]
        return " ".join(args)


def parse_args(args: str) -> Config:
    tokens = shlex.split(args)
    cfg = Config()
    i = 0
    while i < len(tokens):
        token = tokens[i]
        value = tokens[i + 1] if i + 1 < len(tokens) else ""
        if token == "--mock":
            cfg.mock = True
            i += 1
            continue
        if token == "--bike-id":
            try:
                cfg.bike_id = int(value)
            except ValueError:
                pass
        elif token == "--protocols":
            cfg.protocols = [p for p in value.split(",") if p]
        elif token == "--ble-profiles":
            cfg.ble_profiles = [p for p in value.split(",") if p]
        i += 2
    return cfg


def load(path: str = DEFAULTS_FILE) -> Config:
    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return Config()

    for line in lines:
        if ARGS_RE.match(line):
            _, _, value = line.partition("=")
            return parse_args(value.strip().strip('"').strip("'"))
    return Config()


def save(cfg: Config, path: str = DEFAULTS_FILE) -> None:
    """Rewrite only the KTOG_ARGS line, atomically."""
    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    new_line = f'KTOG_ARGS="{cfg.to_args()}"\n'
    for i, line in enumerate(lines):
        if ARGS_RE.match(line):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)

    directory = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            f.writelines(lines)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def setup_done(path: str = SETUP_FLAG) -> bool:
    """Has the wizard already been finished (or skipped) on this Pi?"""
    return os.path.exists(path)


def mark_setup_done(path: str = SETUP_FLAG) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w"):
        pass
