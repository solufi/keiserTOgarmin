# keiserTOgarmin

Un Raspberry Pi qui écoute un vélo **Keiser M3i** et le retransmet à une montre
**Garmin** (Forerunner, Fenix…) comme un capteur de puissance standard.

```
Keiser M3i  ──BLE──►  Raspberry Pi  ──BLE ou ANT+──►  Montre Garmin
```

La montre enregistre puissance, cadence, vitesse et distance dans l'activité,
comme avec un vrai capteur. Rien à installer sur la montre.

## Ce qu'il te faut

- Un Raspberry Pi (Pi 4, Pi 3 ou Zero 2 W) avec **Raspberry Pi OS Bookworm ou
  plus récent**, 64-bit — la version Lite suffit. Les versions plus anciennes
  livrent un Python trop vieux et ne fonctionnent pas.
- Un vélo Keiser M3i (console allumée).
- *Optionnel :* un **Garmin USB ANT Stick** (réf. `010-01058-00`) pour la
  liaison ANT+, plus fiable que le Bluetooth. Les dongles CYCPLUS ne
  fonctionnent pas.

## Installation

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/solufi/keiserTOgarmin.git
cd keiserTOgarmin
sudo ./linux/deploy/install-rpi.sh --hostname ktog
```

Le script installe tout (dépendances, environnement Python, service au
démarrage, règle USB pour l'ANT+) et lance l'interface de configuration.
`--hostname ktog` renomme le Pi pour que la page réponde sur `ktog.local` ;
omets l'option pour garder le nom actuel.

## Configuration

Depuis un téléphone ou un PC sur le même réseau :

```
http://ktog.local:8080/
```

La page est en français ou en anglais : le lien **FR | EN** en haut à droite
mémorise ton choix.

1. **Cherche les vélos** et pédale : le tien est celui dont la cadence bouge.
   Note son *Bike ID*.
2. Saisis ce Bike ID.
3. Choisis la sortie :
   - **Bluetooth — capteur de puissance seul** : sans rien acheter. La montre
     ne verra qu'un capteur, ce qui suffit.
   - **ANT+** : nécessite le dongle USB. Plus stable, et plusieurs appareils
     peuvent capter en même temps. La montre verra **deux** capteurs :
     `PWR` (puissance + cadence) et `SPD` (vitesse + distance).

   Sous chaque choix, la page indique ce que la montre affichera.
4. **Enregistrer et redémarrer**.

Le journal en bas de page doit défiler dès que tu pédales.

## Mettre à jour

Bouton **Mettre à jour** en bas de la page : il récupère la dernière version,
relance l'installeur et redémarre les services. Ta configuration (Bike ID, mode)
est conservée. La page se coupe une dizaine de secondes, le temps que le service
web redémarre : rafraîchis-la, le journal de la mise à jour s'affiche.

En ligne de commande, c'est le même script :

```bash
sudo ~/keiserTOgarmin/linux/deploy/update.sh
```

## Wi-Fi (Pi sans écran ni clavier)

La page comporte un panneau **Wi-Fi** : elle liste les réseaux autour, tu
choisis le tien, tu tapes le mot de passe, et le Pi s'y connecte et s'en
souvient au redémarrage.

Si le Pi démarre sans trouver de réseau connu, il **crée le sien** au bout d'une
quarantaine de secondes :

| Réseau | Mot de passe | Page |
| --- | --- | --- |
| `KeiserToGarmin` | `keiser2garmin` | http://10.42.0.1:8080/ |

Tu t'y connectes avec le téléphone, tu configures le Wi-Fi depuis la page, et le
réseau de secours disparaît. Aucun câble réseau, aucun clavier nécessaire.

## Appairer la montre

Ce n'est **pas** un home trainer : ce sont des capteurs. Sur la montre :
*Paramètres → Capteurs et accessoires → Ajouter*.

- **En Bluetooth** : ajoute un *capteur de puissance*, nommé
  `Keiser M to GATT`.
- **En ANT+** : ajoute **PWR**, puis séparément **SPD**.

Dans les deux cas, règle la **circonférence de roue à 2096 mm**. L'appairage ne
se fait qu'une fois ; ensuite la montre retrouve les capteurs toute seule.

Ensuite, il n'y a plus rien à faire : le Pi démarre le pont automatiquement au
boot. Tu le branches, tu attends une trentaine de secondes, tu pédales.

## Aller plus loin

- [`docs/GUIDE-Pi4-Forerunner955.md`](docs/GUIDE-Pi4-Forerunner955.md) — guide
  pas-à-pas complet, choix Bluetooth vs ANT+, et tableau de dépannage.
- [`linux/README.md`](linux/README.md) — options en ligne de commande,
  fonctionnement interne, détails des protocoles.
- [`DEVELOPMENT.md`](DEVELOPMENT.md) — encodage des trames BLE/ANT+ et
  architecture du code.

Bon à savoir : le Keiser transmet la puissance et la cadence, mais pas la
vitesse. Celle-ci est calculée à partir de la puissance par un modèle physique,
donc elle est plausible mais pas exacte.

## Origine et licence

Ce dépôt est dérivé de [FreeFitness](https://github.com/tao-j/FreeFitness) de
Tao Jin, réduit et adapté au cas Keiser M3i → Garmin sur Raspberry Pi. Le
dossier `mcu/` conserve le firmware ESP32 du projet d'origine ; il n'est pas
utilisé ici.

Copyright (C) 2023-2026 Tao Jin. Logiciel libre sous licence GNU GPL version 3 —
voir [LICENSE](LICENSE). Distribué sans aucune garantie.

Les composants tiers gardent leur propre licence (NimBLE-Arduino : Apache-2.0 ;
M5Unified/M5GFX : MIT ; ant-arduino / antplus-arduino : MIT ; Arduino-ESP32 :
Apache-2.0 / LGPL).
