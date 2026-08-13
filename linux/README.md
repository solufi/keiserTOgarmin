# Linux Implementation (Python)

This directory contains the Python-based implementation of the FreeFitness Data Adapter, designed to run on Linux systems (PC, Raspberry Pi, etc.) using a USB ANT+ dongle and the system's Bluetooth stack.

## Current Implementation and Similar Solutions

[ptx2/gymnasticon](https://github.com/ptx2/gymnasticon) was an earlier project implementing similar functionality, which appears to have been adapted by [k2pi](https://k2pi.company.site/) for their $80-100 commercial product. However, their solution has limited features and is relatively bulky with higher power consumption.

Due to the original JavaScript project's large codebase and unmaintained BLE stack, we've developed this Python-based implementation for better maintainability and extensibility. Our solution adds Keiser bike ID selection and ANT+ speed data transmission.

The Linux implementation successfully interfaces with both Garmin devices (via ANT+) and Apple Watch (via BLE).

## System Design

The system consists of two modules working asynchronously:

1. **`bike`**: Receives sensor data or generates simulated data.
   - Emits a signal when new readings are available.
   - Handles raw data capture from sources like Keiser M3i (BLE advertisement).
2. **`tx`**: Sends the data in BLE or ANT protocol defined format.
   - Handles protocol-specific formatting and timing (typically 4Hz).
   - If no data is received within 2 seconds, transmission should stop.

The encoder `tx.encoder` transforms raw `bike` data into the floating-point values used by `tx`. It performs algorithmic estimations such as:
- **CounterGenerator**: For generating revolution events.
- **Speed Estimation**: Estimating speed from power.
- **Wheel Revolution Estimation**: Estimating wheel revolutions from speed.

## Supported Bikes

### Keiser M3i
Keiser M series BLE broadcast is public ([spec](https://dev.keiser.com/mseries/direct/)). These bikes transmit readings in GAP Manufacturer Specific Data messages. The BikeID of interest can be configured.

### Simulation
Includes a mock source for testing without a physical bike.

## Raspberry Pi deployment

`linux/deploy/` contains an installer that turns a Pi (or any Debian-based SBC)
into an appliance: dependencies in a virtualenv, a systemd unit that survives
reboots, and a udev rule for the ANT+ stick.

```bash
git clone https://github.com/solufi/keiserTOgarmin.git
cd keiserTOgarmin
sudo ./linux/deploy/install-rpi.sh
```

Then set the arguments in `/etc/default/freefitness` and start it:

```bash
FREEFITNESS_ARGS="--bike-id 12 --protocols ant"
sudo systemctl start freefitness
journalctl -u freefitness -f
```

The installer defaults to `--mock --protocols ble`, so a fresh install can be
verified without a bike. Pass `--no-service` to install only the virtualenv and
the udev rule.

The service runs as root: registering GATT services and a pairing agent with
BlueZ over the system bus needs it, and so does the ANT+ USB reset.

### Configuration web UI

The installer also enables `freefitness-web.service`, a standard-library HTTP
server on port 8080 (`web/server.py`) for changing the bike ID and the output
protocol from a phone at the gym:

```
http://<pi-hostname>.local:8080/
```

It rewrites the `FREEFITNESS_ARGS` line of `/etc/default/freefitness` and
restarts the bridge, so the CLI stays the source of truth and the two paths
cannot drift. It also scans for nearby Keiser bikes and lists their IDs with
live cadence, which is how you tell two bikes apart, and tails the journal.

The page is available in French and English (`FR | EN`, remembered in a
cookie), and spells out under each output mode what the watch will end up
pairing with — one `Keiser M to GATT` power sensor over BLE, two sensors over
ANT+ (`PWR` for power and cadence, `SPD` for speed and distance).

Being unauthenticated and able to restart a root service, it belongs on a
trusted LAN only; disable it with
`sudo systemctl disable --now freefitness-web`.

### Choosing an output protocol on a Pi

With BLE output the Pi's single controller has to scan the Keiser (central) and
advertise to the watch (peripheral) at the same time, which is where BlueZ is
least reliable. Two ways to avoid the conflict:

- **ANT+ output** — the radio then does one job each: built-in BLE scans, the
  USB stick transmits. Works with Garmin head units and watches.
- **A second BLE USB dongle** — note that `tx/ble.py` advertises on
  `Adapter.get_first()`, so adapter selection currently depends on enumeration
  order rather than being configurable.

### Selecting BLE profiles

`--ble-profiles` picks which GATT services are registered and advertised:

```bash
python main.py --bike-id 12 --protocols ble --ble-profiles cp
```

Garmin watches expect a power sensor to advertise Cycling Power *alone* — with
CSC also present the PWR search may not bind. CP carries power, cadence and
wheel data, so nothing is lost; the watch derives speed from the wheel
revolutions (set the wheel size to 2096 mm). Leave the default `cp,csc` for
Apple Watch and Zwift.

## Data Transmission Details

### ANT+
Requires an ANT+ transceiver:
- `ANT-USB` (USB `0fcf:1008`)
- `ANT-USBm` (based on nRF24L01P?) — USB `0fcf:1009`, sold as Garmin USB ANT Stick `010-01058-00`
- Other transceivers supporting ANT+ Tx (may need serial driver changes).

*Note: CYCPLUS branded dongles are reported not to work.*

### Bluetooth (BLE GATT)
Linux uses `dbus` to manage `bluez`. The [`bluez-peripheral`](https://github.com/spacecheese/bluez_peripheral) library is used to abstract the peripheral role.

**Known Limitations:**
- The cross-platform solution `bless` has trouble advertising several GATT profiles on Linux. If two profiles are defined, only one may be readable. `bluez-peripheral` is used to mitigate this.
- Bluetooth SIG specs can be difficult to access; community-maintained XML definitions (like [gatt-xml](https://github.com/oesmith/gatt-xml)) are used for bitmask definitions.
