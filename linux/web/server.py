# SPDX-License-Identifier: GPL-3.0-only
"""Tiny configuration UI for the Keiser to Garmin bridge.

Exists so the bike ID and the output protocol can be changed from a phone at
the gym instead of over SSH. It edits KTOG_ARGS in
/etc/default/ktog and restarts ktog.service, i.e. exactly what
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
import os
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import config
import i18n
import scan
import wifi

SERVICE = "ktog.service"
JOURNAL_LINES = 25
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPDATE_SCRIPT = os.path.join(REPO_ROOT, "linux", "deploy", "update.sh")
UPDATE_LOG = "/var/log/ktog-update.log"
UPDATE_LOG_LINES = 20
HOTSPOT_LOG_LINES = 10
WIZARD_STEPS = 4

# key -> (protocols, ble_profiles, pairing-hint string key)
MODES = {
    "ble-cp": (["ble"], ["cp"], "pair_ble_cp"),
    "ble-cp-csc": (["ble"], ["cp", "csc"], "pair_ble_cp_csc"),
    "ant": (["ant"], ["cp"], "pair_ant"),
    "ant-ble": (["ant", "ble"], ["cp"], "pair_ant_ble"),
}


def mode_label_key(mode: str) -> str:
    return "mode_" + mode.replace("-", "_")


def mode_of(cfg: config.Config) -> str:
    for key, (protocols, profiles, _hint) in MODES.items():
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


def journal(lang: str) -> str:
    result = subprocess.run(
        ["journalctl", "-u", SERVICE, "-n", str(JOURNAL_LINES), "--no-pager", "-o", "cat"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip() or i18n.t(lang, "no_output")


STYLE = """
 body { font-family: system-ui, sans-serif; margin: 0 auto; padding: 1.5rem; max-width: 40rem;
        background: #14161a; color: #e8e8e8; }
 h1 { font-size: 1.3rem; }
 fieldset { border: 1px solid #333; border-radius: .5rem; margin: 0 0 1rem; padding: 1rem; }
 label { display: block; margin: .4rem 0; }
 input[type=number] { width: 6rem; font-size: 1.1rem; padding: .3rem; }
 button { font-size: 1rem; padding: .6rem 1rem; margin-right: .5rem; border: 0;
          border-radius: .4rem; background: #2d6cdf; color: #fff; }
 button.secondary { background: #444; }
 pre { background: #0c0e11; padding: .8rem; border-radius: .4rem; overflow-x: auto;
       font-size: .8rem; line-height: 1.35; }
 .state { font-weight: 600; }
 .on { color: #4ade80; } .off { color: #f87171; }
 table { border-collapse: collapse; width: 100%; }
 td, th { text-align: left; padding: .3rem .5rem; border-bottom: 1px solid #333; }
 .hint { margin: 0 0 .9rem 1.6rem; font-size: .85rem; color: #a0a6b0; }
 .langs { float: right; font-size: .9rem; }
 a { color: #8ab4f8; }
 .langs b { color: #e8e8e8; }
 .step { color: #a0a6b0; font-size: .9rem; }
"""

PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Keiser M3i &rarr; Garmin</title>
<style>{style}</style>
</head>
<body>
<div class="langs">{lang_links}</div>
<h1>{title}</h1>
<p>{service}{colon}<span class="state {state_class}">{state}</span></p>

<form method="post" action="/save?lang={lang}">
 <fieldset>
  <legend>{bike}</legend>
  <label>{bike_id_label} <input type="number" name="bike_id" min="0" max="255" value="{bike_id}"></label>
  <label><input type="checkbox" name="mock" {mock_checked}> {mock}</label>
 </fieldset>
 <fieldset>
  <legend>{output}</legend>
  {mode_radios}
 </fieldset>
 <button type="submit">{save}</button>
</form>

<form method="post" action="/scan?lang={lang}">
 <button class="secondary" type="submit">{scan_button}</button>
</form>
{scan_result}

<fieldset>
 <legend>{wifi_title}</legend>
 {wifi_panel}
</fieldset>

<fieldset>
 <legend>{update_title}</legend>
 <p>{version}{colon}<code>{revision}</code></p>
 <form method="post" action="/update?lang={lang}">
  <button class="secondary" type="submit">{update_button}</button>
 </form>
 <p class="hint">{update_hint}</p>
 {update_panel}
</fieldset>

<form method="post" action="/service?lang={lang}">
 <button class="secondary" name="action" value="restart" type="submit">{restart}</button>
 <button class="secondary" name="action" value="stop" type="submit">{stop}</button>
 <button class="secondary" name="action" value="start" type="submit">{start}</button>
</form>

<h2>{journal_title}</h2>
<pre>{journal}</pre>
<p><a href="/?lang={lang}">{refresh}</a>
 &middot; <a href="/setup?lang={lang}">{wizard_link}</a></p>
</body>
</html>
"""

WIZARD_PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Keiser M3i &rarr; Garmin</title>
<style>{style}</style>
</head>
<body>
<div class="langs">{lang_links}</div>
<h1>{title}</h1>
<p class="step">{step_label}</p>
{body}
<form method="post" action="/setup?lang={lang}">
 <button class="secondary" name="action" value="skip" type="submit">{skip}</button>
</form>
<p class="hint">{skip_hint}</p>
</body>
</html>
"""


def render(
    cfg: config.Config,
    lang: str,
    scan_result: str = "",
    wifi_result: str = "",
    networks: list[wifi.Network] | None = None,
    update_result: str = "",
) -> bytes:
    active = service_active()
    wifi_panel = render_wifi(lang, wifi_result, networks)

    return PAGE.format(
        lang=lang,
        style=STYLE,
        lang_links=lang_links(lang, "/"),
        title=html.escape(i18n.t(lang, "title")),
        service=html.escape(i18n.t(lang, "service")),
        colon=i18n.t(lang, "colon"),
        state=html.escape(i18n.t(lang, "active" if active else "inactive")),
        state_class="on" if active else "off",
        bike=html.escape(i18n.t(lang, "bike")),
        bike_id_label=html.escape(i18n.t(lang, "bike_id")),
        bike_id=cfg.bike_id,
        mock=html.escape(i18n.t(lang, "mock")),
        mock_checked="checked" if cfg.mock else "",
        output=html.escape(i18n.t(lang, "output")),
        mode_radios=render_mode_radios(lang, mode_of(cfg)),
        save=html.escape(i18n.t(lang, "save")),
        scan_button=html.escape(i18n.t(lang, "scan_button")),
        scan_result=scan_result,
        wifi_title=html.escape(i18n.t(lang, "wifi")),
        wifi_panel=wifi_panel,
        update_title=html.escape(i18n.t(lang, "update")),
        update_button=html.escape(i18n.t(lang, "update_button")),
        update_hint=html.escape(i18n.t(lang, "update_hint")),
        update_panel=render_update(lang, update_result),
        version=html.escape(i18n.t(lang, "version")),
        revision=html.escape(revision()),
        restart=html.escape(i18n.t(lang, "restart")),
        stop=html.escape(i18n.t(lang, "stop")),
        start=html.escape(i18n.t(lang, "start")),
        journal_title=html.escape(i18n.t(lang, "journal")),
        journal=html.escape(journal(lang)),
        refresh=html.escape(i18n.t(lang, "refresh")),
        wizard_link=html.escape(i18n.t(lang, "wizard_link")),
    ).encode()


def lang_links(lang: str, page: str) -> str:
    return " | ".join(
        f"<b>{code.upper()}</b>"
        if code == lang
        else f'<a href="{page}?lang={code}">{code.upper()}</a>'
        for code in i18n.LANGS
    )


def render_mode_radios(lang: str, selected: str) -> str:
    return "\n".join(
        '<label><input type="radio" name="mode" value="{key}" {checked}> {label}</label>'
        '<p class="hint">{pairing}{colon}{hint}</p>'.format(
            key=key,
            checked="checked" if key == selected else "",
            label=html.escape(i18n.t(lang, mode_label_key(key))),
            pairing=html.escape(i18n.t(lang, "pairing")),
            colon=i18n.t(lang, "colon"),
            # Hints carry <b> markup on purpose; they are author-written, not
            # user input.
            hint=i18n.t(lang, hint_key),
        )
        for key, (_protocols, _profiles, hint_key) in MODES.items()
    )


def revision() -> str:
    result = subprocess.run(
        ["git", "-C", REPO_ROOT, "describe", "--always", "--dirty"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return result.stdout.strip() or "?"


def render_update(lang: str, result: str = "") -> str:
    parts = [result] if result else []
    try:
        with open(UPDATE_LOG) as handle:
            tail = handle.read().splitlines()[-UPDATE_LOG_LINES:]
    except OSError:  # never updated from the page yet
        tail = []
    if tail:
        parts.append(
            "<p>{title}</p><pre>{log}</pre>".format(
                title=html.escape(i18n.t(lang, "update_log")),
                log=html.escape("\n".join(tail)),
            )
        )
    return "\n".join(parts)


def render_wifi(
    lang: str,
    result: str = "",
    networks: list[wifi.Network] | None = None,
    wizard: bool = False,
) -> str:
    """Wi-Fi state, scan and connection form. In wizard mode the forms come
    back to the wizard instead of the configuration page."""
    query = f"lang={lang}&wizard=1" if wizard else f"lang={lang}"
    if not wifi.available():
        return f"<p>{html.escape(i18n.t(lang, 'wifi_unavailable'))}</p>"

    parts = [result] if result else []

    if wifi.hotspot_active():
        parts.append(f"<p class='off'>{html.escape(i18n.t(lang, 'wifi_hotspot'))}</p>")
    else:
        ssid = wifi.current()
        if ssid:
            parts.append(
                "<p>{label}{colon}<b>{ssid}</b></p>".format(
                    label=html.escape(i18n.t(lang, "wifi_connected")),
                    colon=i18n.t(lang, "colon"),
                    ssid=html.escape(ssid),
                )
            )
        else:
            parts.append(
                f"<p class='off'>{html.escape(i18n.t(lang, 'wifi_disconnected'))}</p>"
            )

    parts.append(
        '<form method="post" action="/wifi-scan?{query}">'
        '<button class="secondary" type="submit">{label}</button></form>'.format(
            query=query, label=html.escape(i18n.t(lang, "wifi_scan_button"))
        )
    )

    parts.append(render_hotspot_controls(lang, query))

    if networks is not None:
        if not networks:
            parts.append(f"<p>{html.escape(i18n.t(lang, 'wifi_empty'))}</p>")
        else:
            radios = "\n".join(
                '<label><input type="radio" name="ssid" value="{ssid}" {checked}>'
                " {ssid_text} <span class='hint'>{signal} %{open}</span></label>".format(
                    ssid=html.escape(net.ssid, quote=True),
                    ssid_text=html.escape(net.ssid),
                    checked="checked" if net.active else "",
                    signal=net.signal,
                    open=""
                    if net.secured
                    else " — " + html.escape(i18n.t(lang, "wifi_open")),
                )
                for net in networks
            )
            parts.append(
                '<form method="post" action="/wifi-connect?{query}">'
                "{radios}"
                '<label>{password}<input type="password" name="password"></label>'
                '<button type="submit">{connect}</button>'
                "</form><p class='hint'>{select}</p>".format(
                    query=query,
                    radios=radios,
                    password=html.escape(i18n.t(lang, "wifi_password")) + " ",
                    connect=html.escape(i18n.t(lang, "wifi_connect")),
                    select=html.escape(i18n.t(lang, "wifi_select")),
                )
            )

    return "\n".join(parts)


def render_hotspot_controls(lang: str, query: str) -> str:
    """Access point button (raise or tear down) plus the always-on switch."""
    on = wifi.hotspot_active()
    always = wifi.hotspot_always()
    parts = [
        '<form method="post" action="/hotspot?{query}">'
        '<button class="secondary" name="action" value="{action}" type="submit">'
        "{label}</button></form>"
        '<p class="hint">{hint}</p>'.format(
            query=query,
            action="stop" if on else "start",
            label=html.escape(i18n.t(lang, "hotspot_stop" if on else "hotspot_start")),
            hint=html.escape(
                i18n.t(lang, "hotspot_stop_hint" if on else "hotspot_start_hint")
            ),
        ),
        '<form method="post" action="/hotspot-always?{query}">'
        '<label><input type="checkbox" name="always" {checked}> {label}</label>'
        '<button class="secondary" type="submit">{save}</button></form>'
        '<p class="hint">{hint}</p>'.format(
            query=query,
            checked="checked" if always else "",
            label=html.escape(i18n.t(lang, "hotspot_always")),
            save=html.escape(i18n.t(lang, "save_short")),
            hint=html.escape(i18n.t(lang, "hotspot_always_hint")),
        ),
    ]

    tail = wifi.hotspot_log(HOTSPOT_LOG_LINES)
    if tail:
        parts.append(
            "<p>{title}</p><pre>{log}</pre>".format(
                title=html.escape(i18n.t(lang, "hotspot_log")),
                log=html.escape("\n".join(tail)),
            )
        )
    return "\n".join(parts)


def render_scan(lang: str) -> str:
    try:
        sightings = asyncio.run(scan.scan())
    except Exception as exc:  # a busy or missing adapter must not kill the UI
        return (
            f"<p class='off'>{html.escape(i18n.t(lang, 'scan_failed'))}"
            f"{i18n.t(lang, 'colon')}{html.escape(str(exc))}</p>"
        )

    if not sightings:
        return f"<p>{html.escape(i18n.t(lang, 'scan_empty'))}</p>"

    rows = "\n".join(
        "<tr><td><b>{id}</b></td><td>{cadence:.0f} rpm</td><td>{power} W</td>"
        "<td>{frames} {frames_label}</td></tr>".format(
            id=s.bike_id,
            cadence=s.cadence,
            power=s.power,
            frames=s.frames,
            frames_label=html.escape(i18n.t(lang, "frames")),
        )
        for s in sightings
    )
    return (
        "<table><tr><th>{bike_id}</th><th>{cadence}</th><th>{power}</th><th></th></tr>"
        "{rows}</table><p>{hint}</p>".format(
            bike_id=html.escape(i18n.t(lang, "bike_id")),
            cadence=html.escape(i18n.t(lang, "cadence")),
            power=html.escape(i18n.t(lang, "power")),
            rows=rows,
            hint=html.escape(i18n.t(lang, "scan_hint")),
        )
    )


def bike_id_of(form: dict, cfg: config.Config) -> int:
    """Submitted bike ID, or the stored one when the field is empty/invalid."""
    try:
        return max(0, min(255, int(form.get("bike_id", [""])[0])))
    except ValueError:
        return cfg.bike_id


def wizard_nav(lang: str, step: int, last: bool) -> str:
    """Step form wrapper end: hidden step plus back/next (or finish)."""
    back = (
        '<button class="secondary" name="action" value="back" type="submit">'
        f'{html.escape(i18n.t(lang, "wizard_back"))}</button>'
        if step > 1
        else ""
    )
    return (
        f'<input type="hidden" name="step" value="{step}">'
        f"{back}"
        '<button name="action" value="{action}" type="submit">{label}</button>'.format(
            action="finish" if last else "next",
            label=html.escape(i18n.t(lang, "wizard_finish" if last else "wizard_next")),
        )
    )


def wizard_step_body(
    step: int,
    lang: str,
    cfg: config.Config,
    wifi_result: str,
    networks: list[wifi.Network] | None,
    scan_result: str,
) -> tuple[str, str]:
    """(legend, inner html) of one wizard step."""
    if step == 1:
        # The Wi-Fi panel carries its own forms, so it stays outside the step
        # form: nested forms are not valid HTML.
        return (
            i18n.t(lang, "wifi"),
            "<p class='hint'>{hint}</p>{panel}".format(
                hint=html.escape(i18n.t(lang, "wizard_wifi_hint")),
                panel=render_wifi(lang, wifi_result, networks, wizard=True),
            ),
        )
    if step == 2:
        return (
            i18n.t(lang, "bike"),
            '<p class="hint">{hint}</p>'
            '<button class="secondary" name="action" value="scan" type="submit">'
            "{scan}</button>"
            '<label>{label} <input type="number" name="bike_id" min="0" max="255"'
            ' value="{bike_id}"></label>{result}'.format(
                hint=html.escape(i18n.t(lang, "wizard_bike_hint")),
                scan=html.escape(i18n.t(lang, "scan_button")),
                label=html.escape(i18n.t(lang, "bike_id")),
                bike_id=cfg.bike_id,
                result=scan_result,
            ),
        )
    if step == 3:
        return (
            i18n.t(lang, "output"),
            "<p class='hint'>{hint}</p>{radios}".format(
                hint=html.escape(i18n.t(lang, "wizard_mode_hint")),
                radios=render_mode_radios(lang, mode_of(cfg)),
            ),
        )
    return (
        i18n.t(lang, "pairing"),
        "<p>{summary}{colon}<b>{bike_id_label} {bike_id}</b> — <b>{mode}</b></p>"
        "<p class='hint'>{pairing}{colon}{hint}</p><p class='hint'>{done}</p>".format(
            summary=html.escape(i18n.t(lang, "wizard_summary")),
            colon=i18n.t(lang, "colon"),
            bike_id_label=html.escape(i18n.t(lang, "bike_id")),
            bike_id=cfg.bike_id,
            mode=html.escape(i18n.t(lang, mode_label_key(mode_of(cfg)))),
            pairing=html.escape(i18n.t(lang, "pairing")),
            hint=i18n.t(lang, MODES[mode_of(cfg)][2]),
            done=html.escape(i18n.t(lang, "wizard_finish_hint")),
        ),
    )


def render_wizard(
    step: int,
    lang: str,
    cfg: config.Config,
    wifi_result: str = "",
    networks: list[wifi.Network] | None = None,
    scan_result: str = "",
    message: str = "",
) -> bytes:
    legend, inner = wizard_step_body(step, lang, cfg, wifi_result, networks, scan_result)
    fieldset = "<fieldset><legend>{legend}</legend>{inner}</fieldset>".format(
        legend=html.escape(legend), inner=inner
    )
    fieldset = message + fieldset
    nav = wizard_nav(lang, step, last=step == WIZARD_STEPS)
    if step == 1:
        body = f'{fieldset}<form method="post" action="/setup?lang={lang}">{nav}</form>'
    else:
        body = (
            f'<form method="post" action="/setup?lang={lang}">{fieldset}{nav}</form>'
        )

    return WIZARD_PAGE.format(
        lang=lang,
        style=STYLE,
        lang_links=lang_links(lang, "/setup"),
        title=html.escape(i18n.t(lang, "wizard_title")),
        step_label=html.escape(
            i18n.t(lang, "wizard_step").format(step=step, total=WIZARD_STEPS)
        ),
        body=body,
        skip=html.escape(i18n.t(lang, "wizard_skip")),
        skip_hint=html.escape(i18n.t(lang, "wizard_skip_hint")),
    ).encode()


class Handler(BaseHTTPRequestHandler):
    server_version = "ktog-web"

    def _lang(self) -> str:
        """?lang= wins, else the cookie set on the last explicit choice."""
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "lang" in query:
            return i18n.normalize(query["lang"][0])
        cookies = self.headers.get("Cookie") or ""
        for part in cookies.split(";"):
            name, _, value = part.strip().partition("=")
            if name == "lang":
                return i18n.normalize(value)
        return i18n.DEFAULT_LANG

    def _wizard(self) -> bool:
        """Should a Wi-Fi or hotspot form answer inside the wizard?"""
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        return query.get("wizard", [""])[0] == "1"

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        lang = self._lang()
        if path == "/setup":
            self._send(render_wizard(1, lang, config.load()))
        elif path == "/":
            if not config.setup_done():
                self._redirect(lang, "/setup")
                return
            self._send(render(config.load(), lang))
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        # keep_blank_values: a number input the browser considers invalid is
        # submitted empty, and dropping it would look like "bike_id 0".
        form = urllib.parse.parse_qs(
            self.rfile.read(length).decode(), keep_blank_values=True
        )
        path = urllib.parse.urlparse(self.path).path
        lang = self._lang()

        if path == "/save":
            self._save(form, lang)
        elif path == "/scan":
            self._send(render(config.load(), lang, render_scan(lang)))
        elif path == "/wifi-scan":
            self._wifi_scan(lang)
        elif path == "/wifi-connect":
            self._wifi_connect(form, lang)
        elif path == "/hotspot":
            self._hotspot(form, lang)
        elif path == "/hotspot-always":
            self._hotspot_always(form, lang)
        elif path == "/setup":
            self._setup(form, lang)
        elif path == "/update":
            self._update(lang)
        elif path == "/service":
            action = form.get("action", ["restart"])[0]
            if action in ("start", "stop", "restart"):
                systemctl(action, SERVICE)
            self._redirect(lang)
        else:
            self.send_error(404)

    def _wifi_page(
        self, lang: str, result: str, networks: list[wifi.Network] | None = None
    ):
        """Answer a Wi-Fi form, on whichever page it was submitted from."""
        cfg = config.load()
        if self._wizard():
            self._send(render_wizard(1, lang, cfg, wifi_result=result, networks=networks))
        else:
            self._send(render(cfg, lang, wifi_result=result, networks=networks))

    def _wifi_scan(self, lang: str):
        try:
            networks = wifi.scan()
            error = ""
        except Exception as exc:  # nmcli missing, busy or rfkill'd
            networks, error = [], (
                f"<p class='off'>{html.escape(i18n.t(lang, 'scan_failed'))}"
                f"{i18n.t(lang, 'colon')}{html.escape(str(exc))}</p>"
            )
        self._wifi_page(lang, error, networks)

    def _wifi_connect(self, form: dict, lang: str):
        ssid = form.get("ssid", [""])[0]
        password = form.get("password", [""])[0]
        try:
            wifi.connect(ssid, password)
        except Exception as exc:
            # Joining a network usually kills the very connection carrying this
            # request when the client is on the setup hotspot, so the answer may
            # never arrive — the page is only best-effort feedback.
            result = (
                f"<p class='off'>{html.escape(i18n.t(lang, 'wifi_failed'))}"
                f"{i18n.t(lang, 'colon')}{html.escape(str(exc))}</p>"
            )
        else:
            result = (
                f"<p class='on'>{html.escape(i18n.t(lang, 'wifi_ok'))}"
                f"{i18n.t(lang, 'colon')}<b>{html.escape(ssid)}</b></p>"
            )
        self._wifi_page(lang, result)

    def _hotspot(self, form: dict, lang: str):
        """Switch the access point on or off. The answer goes out first: the
        switch drops whichever network is carrying this request."""
        action = form.get("action", [""])[0]
        if action not in ("start", "stop"):
            self.send_error(400)
            return
        on = action == "start"
        try:
            wifi.switch_hotspot(on)
        except Exception as exc:  # unwritable log, missing script
            result = f"<p class='off'>{html.escape(str(exc))}</p>"
        else:
            result = "<p class='on'>{msg}</p>".format(
                msg=html.escape(
                    i18n.t(lang, "hotspot_starting" if on else "hotspot_stopping")
                )
            )
        self._wifi_page(lang, result)

    def _hotspot_always(self, form: dict, lang: str):
        try:
            wifi.set_hotspot_always("always" in form)
        except Exception as exc:
            result = f"<p class='off'>{html.escape(str(exc))}</p>"
        else:
            result = f"<p class='on'>{html.escape(i18n.t(lang, 'saved'))}</p>"
        self._wifi_page(lang, result)

    def _setup(self, form: dict, lang: str):
        """One wizard step: apply what it collected, then move on."""
        try:
            step = int(form.get("step", ["1"])[0])
        except ValueError:
            step = 1
        step = max(1, min(WIZARD_STEPS, step))
        action = form.get("action", [""])[0]
        cfg = config.load()

        if action == "scan":
            self._send(render_wizard(step, lang, cfg, scan_result=render_scan(lang)))
            return
        if action not in ("next", "back", "finish", "skip"):
            self.send_error(400)
            return

        try:
            if action == "next" and step == 2:
                cfg.bike_id = bike_id_of(form, cfg)
                config.save(cfg)
            elif action == "next" and step == 3:
                protocols, profiles, _hint = MODES.get(
                    form.get("mode", [""])[0], MODES["ble-cp"]
                )
                cfg.protocols = list(protocols)
                cfg.ble_profiles = list(profiles)
                config.save(cfg)
            if action in ("finish", "skip"):
                config.mark_setup_done()
        except OSError as exc:  # not running as root, read-only filesystem
            self._send(
                render_wizard(
                    step,
                    lang,
                    cfg,
                    message=f"<p class='off'>{html.escape(str(exc))}</p>",
                )
            )
            return

        if action in ("finish", "skip"):
            if action == "finish":
                systemctl("restart", SERVICE)
            self._redirect(lang)
            return

        self._send(
            render_wizard(step + (1 if action == "next" else -1), lang, config.load())
        )

    def _update(self, lang: str):
        """Start update.sh detached: it restarts this very service at the end."""
        try:
            log = open(UPDATE_LOG, "w")
        except OSError as exc:
            self._send(
                render(
                    config.load(),
                    lang,
                    update_result=f"<p class='off'>{html.escape(str(exc))}</p>",
                )
            )
            return

        with log:
            subprocess.Popen(
                ["/bin/bash", UPDATE_SCRIPT],
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                cwd=REPO_ROOT,
            )
        self._send(
            render(
                config.load(),
                lang,
                update_result=(
                    f"<p class='on'>{html.escape(i18n.t(lang, 'update_started'))}</p>"
                ),
            )
        )

    def _save(self, form: dict, lang: str):
        cfg = config.load()
        cfg.bike_id = bike_id_of(form, cfg)
        cfg.mock = "mock" in form
        protocols, profiles, _hint = MODES.get(
            form.get("mode", [""])[0], MODES["ble-cp"]
        )
        cfg.protocols = list(protocols)
        cfg.ble_profiles = list(profiles)

        config.save(cfg)
        systemctl("restart", SERVICE)
        self._redirect(lang)

    def _send(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header(
            "Set-Cookie", f"lang={self._lang()}; Path=/; Max-Age=31536000; SameSite=Lax"
        )
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, lang: str, page: str = "/"):
        self.send_response(303)
        self.send_header("Location", f"{page}?lang={lang}")
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
