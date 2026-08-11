# SPDX-License-Identifier: GPL-3.0-only
"""Passive scan for nearby Keiser M3i bikes, for the web UI's bike picker.

Decodes the same manufacturer-specific data as bike/keiser.py (ID 0x0102,
bike id at byte 3) but keeps every bike it hears instead of filtering on one
id, so the user can pick theirs from a list. Cadence is what tells two bikes
apart: pedal, and only yours moves.
"""

import asyncio
import struct

from bleak import BleakScanner

KEISER_MANUFACTURER_ID = 0x0102
FRAME_LEN = 17


class BikeSighting:
    def __init__(self, bike_id: int, name: str, address: str):
        self.bike_id = bike_id
        self.name = name
        self.address = address
        self.cadence = 0.0
        self.power = 0
        self.frames = 0


def decode(frame: bytes) -> tuple[int, float, int] | None:
    """Return (bike_id, cadence_rpm, power_w) for a real-time Keiser frame."""
    if len(frame) != FRAME_LEN or frame[2] != 0:
        return None
    bike_id, cadence, _hr, power = struct.unpack_from("<BHHH", frame, 3)
    return bike_id, cadence / 10, power


async def scan(seconds: float = 12.0) -> list[BikeSighting]:
    seen: dict[int, BikeSighting] = {}

    def callback(device, advertisement_data):
        frame = advertisement_data.manufacturer_data.get(KEISER_MANUFACTURER_ID)
        if frame is None:
            return
        decoded = decode(bytes(frame))
        if decoded is None:
            return
        bike_id, cadence, power = decoded
        sighting = seen.setdefault(
            bike_id, BikeSighting(bike_id, device.name or "?", device.address)
        )
        sighting.cadence = cadence
        sighting.power = power
        sighting.frames += 1

    async with BleakScanner(callback):
        await asyncio.sleep(seconds)

    return sorted(seen.values(), key=lambda s: s.bike_id)
