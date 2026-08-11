# Keiser M3i → Raspberry Pi 4 → Forerunner 955

Guide taillé pour cette configuration exacte. Compte 30 minutes, dont 20
d'attente.

Deux chemins, selon le matériel disponible :

| | Bluetooth (§4a) | ANT+ (§4b) |
|---|---|---|
| Matériel | rien de plus que le Pi | dongle USB ANT+ |
| Capteurs sur la montre | 1 (PWR) | 2 (PWR + SPD) |
| Risque | la radio du Pi scanne *et* annonce en même temps — point faible de BlueZ | aucun conflit, chaque radio a un rôle |

Commence par le Bluetooth : c'est gratuit et immédiat. Si la 955 refuse de se
connecter ou décroche, passe à l'ANT+.

## 0. Matériel

- Raspberry Pi 4 (déjà en stock) + microSD + alim USB-C
- *Optionnel :* Garmin USB ANT Stick réf. **010-01058-00** (= ANTUSB-m, USB `0fcf:1009`)
- **Système : Raspberry Pi OS Bookworm ou plus récent.** Obligatoire : le code
  utilise `asyncio.TaskGroup`, apparu en Python 3.11. Bullseye (Python 3.9)
  échoue au démarrage. L'installeur vérifie la version et refuse de continuer.

Aucun dongle Bluetooth supplémentaire n'est nécessaire dans les deux cas.

## 1. Installation sur le Pi

```bash
sudo apt update && sudo apt full-upgrade -y
git clone https://github.com/solufi/keiserTOgarmin.git
cd keiserTOgarmin
sudo ./linux/deploy/install-rpi.sh
```

Le script installe `bluez`, `libusb`, crée un virtualenv `.venv`, installe la
règle udev du dongle ANT+ et enregistre le service systemd (activé au
démarrage, mais pas encore lancé).

## 2. Trouver le Bike ID de ton vélo

Il s'affiche sur la console du Keiser M3i. En cas de doute, écoute ce qui passe
autour de toi :

```bash
cd ~/keiserTOgarmin/linux
sudo ../.venv/bin/python -c "
import asyncio
from bleak import BleakScanner
def cb(d, ad):
    msd = ad.manufacturer_data.get(0x0102)
    if msd: print(d.address, 'bike_id =', msd[3], '| cadence', int.from_bytes(msd[4:6],'little')/10, 'rpm')
async def m():
    async with BleakScanner(cb): await asyncio.sleep(20)
asyncio.run(m())
"
```

Pédale sur le vélo qui t'intéresse : c'est celui dont la cadence bouge.

## 3. Configurer et démarrer

```bash
sudo nano /etc/default/freefitness
```

Remplace la ligne par (avec ton numéro), **sans dongle ANT+** :

```
FREEFITNESS_ARGS="--bike-id 12 --protocols ble --ble-profiles cp"
```

Ou, **avec le dongle ANT+** :

```
FREEFITNESS_ARGS="--bike-id 12 --protocols ant"
```

Puis :

```bash
sudo systemctl start freefitness
journalctl -u freefitness -f
```

Dès que tu pédales, tu dois voir défiler `BLE 2A63 CP | pwr 143 W | ...` (ou
`ANT 0x10 PWR | ...`). Si tu vois `No data` en boucle, le Pi n'entend pas le
vélo : mauvais bike ID, ou trop loin.

## 4a. Apparier en Bluetooth

Un seul capteur à ajouter : le profil Cycling Power transporte puissance,
cadence **et** tours de roue. `--ble-profiles cp` masque le profil CSC, que les
Garmin digèrent mal quand il accompagne le CP.

Sur la montre : **Paramètres → Capteurs et accessoires → Ajouter → Capteur de
puissance**. Le pont apparaît sous le nom `Keiser M to GATT`. Règle ensuite la
**circonférence de roue à 2096 mm** (700x25c), sinon vitesse et distance sont
fausses — la vitesse est déduite de la puissance par un modèle physique, pas
mesurée.

## 4b. Apparier en ANT+

Ce ne sont **pas** des home trainers, ce sont deux capteurs distincts. Sur la
montre : **Paramètres → Capteurs et accessoires → Ajouter**, puis :

1. Cherche **PWR** (capteur de puissance) → apparier.
2. Reviens dans Ajouter, cherche **SPD** (capteur de vitesse) → apparier.
3. Sur le capteur de vitesse, règle la **circonférence de roue à 2096 mm**.

Une fois appariés, la montre les retrouve automatiquement aux séances
suivantes.

## 5. Usage courant

Rien à reconfigurer : le service démarre au boot et se relance seul en cas de
plantage. Tu branches le Pi, tu attends ~30 s, tu lances la séance vélo sur la
montre, tu pédales.

Seul cas nécessitant une intervention : changer de vélo dans la salle (bike ID
différent) → édite `/etc/default/freefitness` et
`sudo systemctl restart freefitness`.

## 6. Dépannage

| Symptôme | Piste |
|---|---|
| `No ANT devices available` | Dongle mal détecté : `lsusb \| grep 0fcf` doit montrer `1008` ou `1009`. Débranche/rebranche après l'install (la règle udev ne s'applique qu'à la connexion). |
| `ANT: No data` en boucle | Mauvais bike ID (étape 2), ou le Pi est trop loin du vélo. |
| La montre ne trouve rien | Vérifie que le journal affiche bien des trames PWR. La montre doit chercher un capteur, pas un home trainer. |
| En BLE : la montre voit le capteur puis décroche | C'est le conflit scan/annonce sur une seule radio. Bascule sur l'ANT+, ou ajoute un 2e dongle BLE. |
| En BLE : rien n'apparaît du tout | Vérifie `--ble-profiles cp` (sans le CSC) et que `systemctl is-active bluetooth` répond `active`. |
| Vitesse/distance farfelues | Circonférence de roue ≠ 2096 mm. |
| Le service échoue au boot | `journalctl -u freefitness -b` ; si l'erreur mentionne Python 3.9/3.10, ton OS est trop vieux (Bookworm requis). |

## Ce qui n'a pas été testé

J'ai validé sur ma machine : l'installeur, le service systemd, et la chaîne
source → encodeur (puissance, cadence, compteurs de tours qui s'incrémentent
correctement). Je **n'ai pas pu** tester l'émission ANT+ réelle (pas de dongle)
ni l'émission BLE (pas de contrôleur Bluetooth sur ma VM). Le premier essai
avec ton dongle sera le vrai test — envoie-moi le journal si ça bloque.
