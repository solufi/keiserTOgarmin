# SPDX-License-Identifier: GPL-3.0-only
"""French/English strings for the configuration UI.

Flat dict per language rather than gettext: a handful of strings does not
justify compiling .mo files onto the Pi. `t()` falls back to French, then to
the key itself, so a missing translation degrades instead of raising.
"""

DEFAULT_LANG = "fr"
LANGS = ("fr", "en")

STRINGS = {
    "fr": {
        "title": "Keiser M3i → Garmin",
        # French puts a thin space before a colon; English does not.
        "colon": "&nbsp;: ",
        "service": "Service",
        "active": "actif",
        "inactive": "arrêté",
        "bike": "Vélo",
        "bike_id": "Bike ID",
        "mock": "Simulateur (ignore le vélo, données factices)",
        "output": "Sortie vers la montre",
        "save": "Enregistrer et redémarrer",
        "scan_button": "Chercher les vélos (12 s)",
        "restart": "Redémarrer",
        "stop": "Arrêter",
        "start": "Démarrer",
        "journal": "Journal",
        "refresh": "Rafraîchir",
        "no_output": "(aucune sortie)",
        "scan_failed": "Scan impossible",
        "scan_empty": "Aucun vélo entendu. Réveille la console du Keiser en"
        " pédalant et réessaie.",
        "scan_hint": "Le tien est celui dont la cadence bouge quand tu pédales.",
        "cadence": "Cadence",
        "power": "Puissance",
        "frames": "trames",
        "pairing": "Sur la montre",
        "mode_ble_cp": "Bluetooth — capteur de puissance seul (Garmin)",
        "mode_ble_cp_csc": "Bluetooth — puissance + vitesse/cadence (Zwift,"
        " Apple Watch)",
        "mode_ant": "ANT+ (dongle USB requis)",
        "mode_ant_ble": "ANT+ et Bluetooth simultanément",
        "pair_ble_cp": "1 capteur de puissance à ajouter, nommé"
        " « Keiser M to GATT » : il porte la puissance, la cadence et les tours"
        " de roue.",
        "pair_ble_cp_csc": "2 capteurs Bluetooth : « Keiser M to GATT » en"
        " puissance et en vitesse/cadence. À éviter sur Garmin, qui peut alors"
        " ne pas trouver le capteur de puissance.",
        "pair_ant": "2 capteurs ANT+ à ajouter séparément : <b>PWR</b>"
        " (puissance + cadence) et <b>SPD</b> (vitesse + distance). Règle la"
        " circonférence de roue à 2096 mm sur le capteur de vitesse.",
        "pair_ant_ble": "Les capteurs ANT+ <b>PWR</b> et <b>SPD</b> et le"
        " capteur Bluetooth « Keiser M to GATT » sont émis en même temps :"
        " apparie ce que ton appareil préfère.",
        "wifi": "Wi-Fi",
        "wifi_connected": "Connecté à",
        "wifi_disconnected": "Non connecté",
        "wifi_hotspot": "Le Pi diffuse son propre réseau de configuration."
        " Choisis ton Wi-Fi ci-dessous : la connexion à ce réseau de secours"
        " sera coupée, rejoins ton Wi-Fi habituel puis rouvre la page sur"
        " http://ktog.local:8080/",
        "wifi_scan_button": "Chercher les réseaux Wi-Fi",
        "wifi_password": "Mot de passe",
        "wifi_connect": "Se connecter",
        "wifi_select": "Choisis un réseau, puis saisis le mot de passe.",
        "wifi_empty": "Aucun réseau trouvé.",
        "wifi_failed": "Connexion impossible",
        "wifi_ok": "Connecté au réseau",
        "wifi_open": "réseau ouvert",
        "wifi_unavailable": "NetworkManager est absent : configure le Wi-Fi"
        " avec raspi-config.",
        "update": "Mise à jour",
        "update_button": "Mettre à jour",
        "update_hint": "Récupère la dernière version et relance l'installeur."
        " La page se coupe une dizaine de secondes : rafraîchis-la pour voir la"
        " suite. Ta configuration est conservée.",
        "update_started": "Mise à jour lancée. Rafraîchis la page dans une"
        " minute.",
        "update_log": "Journal de la dernière mise à jour",
        "version": "Version",
    },
    "en": {
        "title": "Keiser M3i → Garmin",
        "colon": ": ",
        "service": "Service",
        "active": "running",
        "inactive": "stopped",
        "bike": "Bike",
        "bike_id": "Bike ID",
        "mock": "Simulator (ignore the bike, generate fake data)",
        "output": "Output to the watch",
        "save": "Save and restart",
        "scan_button": "Scan for bikes (12 s)",
        "restart": "Restart",
        "stop": "Stop",
        "start": "Start",
        "journal": "Log",
        "refresh": "Refresh",
        "no_output": "(no output)",
        "scan_failed": "Scan failed",
        "scan_empty": "No bike heard. Wake the Keiser console up by pedalling"
        " and try again.",
        "scan_hint": "Yours is the one whose cadence moves while you pedal.",
        "cadence": "Cadence",
        "power": "Power",
        "frames": "frames",
        "pairing": "On the watch",
        "mode_ble_cp": "Bluetooth — power sensor only (Garmin)",
        "mode_ble_cp_csc": "Bluetooth — power + speed/cadence (Zwift, Apple"
        " Watch)",
        "mode_ant": "ANT+ (USB stick required)",
        "mode_ant_ble": "ANT+ and Bluetooth at the same time",
        "pair_ble_cp": "1 power sensor to add, named “Keiser M to GATT”: it"
        " carries power, cadence and wheel revolutions.",
        "pair_ble_cp_csc": "2 Bluetooth sensors: “Keiser M to GATT” as power"
        " and as speed/cadence. Avoid on Garmin, which may then fail to find"
        " the power sensor.",
        "pair_ant": "2 ANT+ sensors to add separately: <b>PWR</b> (power +"
        " cadence) and <b>SPD</b> (speed + distance). Set the wheel"
        " circumference to 2096 mm on the speed sensor.",
        "pair_ant_ble": "The ANT+ <b>PWR</b> and <b>SPD</b> sensors and the"
        " Bluetooth “Keiser M to GATT” sensor are broadcast together: pair"
        " whichever your device prefers.",
        "wifi": "Wi-Fi",
        "wifi_connected": "Connected to",
        "wifi_disconnected": "Not connected",
        "wifi_hotspot": "The Pi is broadcasting its own setup network. Pick"
        " your Wi-Fi below: this fallback network will go away, so rejoin your"
        " usual Wi-Fi and reopen the page at http://ktog.local:8080/",
        "wifi_scan_button": "Scan for Wi-Fi networks",
        "wifi_password": "Password",
        "wifi_connect": "Connect",
        "wifi_select": "Pick a network, then type the password.",
        "wifi_empty": "No network found.",
        "wifi_failed": "Could not connect",
        "wifi_ok": "Connected to network",
        "wifi_open": "open network",
        "wifi_unavailable": "NetworkManager is missing: configure Wi-Fi with"
        " raspi-config.",
        "update": "Update",
        "update_button": "Update now",
        "update_hint": "Fetches the latest version and re-runs the installer."
        " The page drops for about ten seconds: refresh it to see the rest."
        " Your configuration is kept.",
        "update_started": "Update started. Refresh the page in a minute.",
        "update_log": "Last update log",
        "version": "Version",
    },
}


def normalize(lang: str | None) -> str:
    return lang if lang in LANGS else DEFAULT_LANG


def t(lang: str, key: str) -> str:
    return STRINGS.get(lang, {}).get(key) or STRINGS[DEFAULT_LANG].get(key, key)
