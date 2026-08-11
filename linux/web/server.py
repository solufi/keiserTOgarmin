# SPDX-License-Identifier: GPL-3.0-only
"""Tiny configuration UI for the FreeFitness bridge.

Exists so the bike ID and the output protocol can be changed from a phone at
the gym instead of over SSH. It edits FREEFITNESS_ARGS in
/etc/default/freefitness and restarts freefitness.service, i.e. exactly what
the manual procedure does — so the CLI stays the source of truth and the two
paths cannot drift.

Standard library only (no Flask): the venv already exists for the bridge and
one dependency-free file is easier to keep running unattended.

Usage:  sudo .venv/bin/python web/server.py [--port 8080]

The listener is unauthenticated and can restart a root service, so bind it to
a trusted LAN only.
"""

import argparse
import asyncio
import html
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import config
import scan

SERVICE = "freefitness.service"
JOURNAL_LINES = 25

MODES = {
    "ble-cp": ("Bluetooth — capteur de puissance seul (Garmin)", ["ble"], ["cp"]),
    "ble-cp-csc": ("Bluetooth — puissance + vitesse/cadence (Zwift, Apple Watch)", ["ble"], ["cp", "csc"]),
    "ant": ("ANT+ (dongle USB requis)", ["ant"], ["cp"]),
    "ant-ble": ("ANT+ et Bluetooth simultanément", ["ant", "ble"], ["cp"]),
}


def mode_of(cfg: config.Config) -> str:
    for key, (_label, protocols, profiles) in MODES.items():
        if protocols == cfg.protocols and (
            "ble" not in protocols or profiles == cfg.ble_profiles
        ):
            return key
    return "ble-cp"


def systemctl(*args: str) -> str:
    result = subprocess.run(
        ["systemctl", *args], capture_output=True, text=True, timeout=30
    )
    return (result.stdout + result.stderr).strip()


def service_active() -> bool:
    return systemctl("is-active", SERVICE) == "active"


def journal() -> str:
    result = subprocess.run(
        ["journalctl", "-u", SERVICE, "-n", str(JOURNAL_LINES), "--no-pager", "-o", "cat"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip() or "(aucune sortie)"


PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Keiser to Garmin</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 0 auto; padding: 1.5rem; max-width: 40rem;
        background: #14161a; color: #e8e8e8; }}
 h1 {{ font-size: 1.3rem; }}
 fieldset {{ border: 1px solid #333; border-radius: .5rem; margin: 0 0 1rem; padding: 1rem; }}
 label {{ display: block; margin: .4rem 0; }}
 input[type=number] {{ width: 6rem; font-size: 1.1rem; padding: .3rem; }}
 button {{ font-size: 1rem; padding: .6rem 1rem; margin-right: .5rem; border: 0;
           border-radius: .4rem; background: #2d6cdf; color: #fff; }}
 button.secondary {{ background: #444; }}
 pre {{ background: #0c0e11; padding: .8rem; border-radius: .4rem; overflow-x: auto;
        font-size: .8rem; line-height: 1.35; }}
 .state {{ font-weight: 600; }}
 .on {{ color: #4ade80; }} .off {{ color: #f87171; }}
 table {{ border-collapse: collapse; width: 100%; }}
 td, th {{ text-align: left; padding: .3rem .5rem; border-bottom: 1px solid #333; }}
</style>
</head>
<body>
<h1>Keiser M3i → Garmin</h1>
<p>Service : <span class="state {state_class}">{state}</span></p>

<form method="post" action="/save">
 <fieldset>
  <legend>Vélo</legend>
  <label>Bike ID <input type="number" name="bike_id" min="0" max="255" value="{bike_id}"></label>
  <label><input type="checkbox" name="mock" {mock_checked}> Simulateur (ignore le vélo, données factices)</label>
 </fieldset>
 <fieldset>
  <legend>Sortie vers la montre</legend>
  {mode_radios}
 </fieldset>
 <button type="submit">Enregistrer et redémarrer</button>
</form>

<form method="post" action="/scan">
 <button class="secondary" type="submit">Chercher les vélos (12 s)</button>
</form>
{scan_result}

<form method="post" action="/service">
 <button class="secondary" name="action" value="restart" type="submit">Redémarrer</button>
 <button class="secondary" name="action" value="stop" type="submit">Arrêter</button>
 <button class="secondary" name="action" value="start" type="submit">Démarrer</button>
</form>

<h2>Journal</h2>
<pre>{journal}</pre>
<p><a href="/" style="color:#8ab4f8">Rafraîchir</a></p>
</body>
</html>
"""


def render(cfg: config.Config, scan_result: str = "") -> bytes:
    active = service_active()
    selected = mode_of(cfg)
    radios = "\n".join(
        '<label><input type="radio" name="mode" value="{key}" {checked}> {label}</label>'.format(
            key=key,
            label=html.escape(label),
            checked="checked" if key == selected else "",
        )
        for key, (label, _p, _f) in MODES.items()
    )
    return PAGE.format(
        state="actif" if active else "arrêté",
        state_class="on" if active else "off",
        bike_id=cfg.bike_id,
        mock_checked="checked" if cfg.mock else "",
        mode_radios=radios,
        scan_result=scan_result,
        journal=html.escape(journal()),
    ).encode()


def render_scan() -> str:
    try:
        sightings = asyncio.run(scan.scan())
    except Exception as exc:  # a busy or missing adapter must not kill the UI
        return f"<p class='off'>Scan impossible : {html.escape(str(exc))}</p>"

    if not sightings:
        return (
            "<p>Aucun vélo entendu. Réveille la console du Keiser en pédalant"
            " et réessaie.</p>"
        )

    rows = "\n".join(
        "<tr><td><b>{id}</b></td><td>{cadence:.0f} rpm</td><td>{power} W</td>"
        "<td>{frames} trames</td></tr>".format(
            id=s.bike_id, cadence=s.cadence, power=s.power, frames=s.frames
        )
        for s in sightings
    )
    return (
        "<table><tr><th>Bike ID</th><th>Cadence</th><th>Puissance</th><th></th></tr>"
        f"{rows}</table><p>Le tien est celui dont la cadence bouge quand tu pédales.</p>"
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "freefitness-web"

    def do_GET(self):
        if self.path.split("?")[0] != "/":
            self.send_error(404)
            return
        self._send(render(config.load()))

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        form = urllib.parse.parse_qs(self.rfile.read(length).decode())
        path = self.path.split("?")[0]

        if path == "/save":
            self._save(form)
        elif path == "/scan":
            self._send(render(config.load(), render_scan()))
        elif path == "/service":
            action = form.get("action", ["restart"])[0]
            if action in ("start", "stop", "restart"):
                systemctl(action, SERVICE)
            self._redirect()
        else:
            self.send_error(404)

    def _save(self, form: dict):
        cfg = config.load()
        try:
            bike_id = int(form.get("bike_id", ["0"])[0])
        except ValueError:
            bike_id = cfg.bike_id
        cfg.bike_id = max(0, min(255, bike_id))
        cfg.mock = "mock" in form
        _label, protocols, profiles = MODES.get(
            form.get("mode", [""])[0], MODES["ble-cp"]
        )
        cfg.protocols = list(protocols)
        cfg.ble_profiles = list(profiles)

        config.save(cfg)
        systemctl("restart", SERVICE)
        self._redirect()

    def _send(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self):
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


def parse_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli()
    print(f"Configuration UI on http://{args.host}:{args.port}/", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
