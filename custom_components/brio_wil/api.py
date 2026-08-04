"""Low-level TCP client for CCEI BRiO WiL pool lights.

Reverse engineered from the Node-RED flow at
https://github.com/cRemE-fReSh/BRiO-WiL-Integration-for-Home-Assistant, which
is the only public documentation of this protocol. The device listens on a
single TCP port (30302 by default):

- Sending an empty payload returns a fixed-offset ASCII status telegram.
- Sending a small JSON object changes a single aspect of the light:
  ``{"prcn": <mode>}`` (color/pattern), ``{"plum": <level>}`` (brightness),
  ``{"pspd": <speed>}`` (pattern sequence speed) or ``{"sprj": 0|1}`` (power).

There is no explicit "set power" command, only a toggle, so callers must only
send ``sprj`` when the desired state actually differs from the last known
one. None of this has been verified against real hardware yet; the status
telegram offsets in particular are a best-effort port of the Node-RED
``substring``/``parseInt`` calls and may need correcting once tested.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
import logging

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 30302
DEFAULT_TIMEOUT = 5

# Offsets into the ASCII status telegram, ported from the Node-RED flow's
# `msg.payload.substring(...)` calls.
_STATE_OFFSET = 33
_MODE_OFFSET = 64
_SPEED_OFFSET = 70
_BRIGHTNESS_OFFSET = 71
_MIN_TELEGRAM_LENGTH = _BRIGHTNESS_OFFSET + 1


class BrioWilError(Exception):
    """Raised when the device cannot be reached or replies unexpectedly."""


@dataclass
class BrioWilStatus:
    """Parsed status telegram from a BRiO WiL device."""

    raw: str
    state: int
    mode: int
    speed: int
    brightness: int

    @property
    def is_on(self) -> bool:
        """Return whether the light is currently on."""
        return self.state != 0


def _parse_status(raw: str) -> BrioWilStatus:
    """Parse the fixed-offset status telegram returned by the device."""
    if len(raw) < _MIN_TELEGRAM_LENGTH:
        raise BrioWilError(f"Status telegram too short ({len(raw)} bytes): {raw!r}")
    try:
        state = int(raw[_STATE_OFFSET : _STATE_OFFSET + 1])
        mode = int(raw[_MODE_OFFSET : _MODE_OFFSET + 2], 16)
        speed = int(raw[_SPEED_OFFSET : _SPEED_OFFSET + 1], 16) - 4
        brightness = int(raw[_BRIGHTNESS_OFFSET : _BRIGHTNESS_OFFSET + 1], 16) // 4
    except ValueError as err:
        raise BrioWilError(f"Could not parse status telegram: {raw!r}") from err
    return BrioWilStatus(
        raw=raw, state=state, mode=mode, speed=speed, brightness=brightness
    )


class BrioWilClient:
    """Speak the BRiO WiL raw-TCP/JSON control protocol."""

    def __init__(
        self, host: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._timeout = timeout

    async def _async_send(self, payload: str) -> bytes:
        """Open a connection, send payload, and collect the reply until idle."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
        except (OSError, TimeoutError) as err:
            raise BrioWilError(
                f"Could not connect to {self._host}:{self._port}"
            ) from err

        try:
            writer.write(payload.encode("ascii"))
            await writer.drain()

            chunks = bytearray()
            with contextlib.suppress(TimeoutError):
                while True:
                    chunk = await asyncio.wait_for(
                        reader.read(4096), timeout=self._timeout
                    )
                    if not chunk:
                        break
                    chunks.extend(chunk)
        except OSError as err:
            raise BrioWilError(
                f"Communication with {self._host}:{self._port} failed"
            ) from err
        finally:
            writer.close()
            with contextlib.suppress(OSError):
                await writer.wait_closed()

        return bytes(chunks)

    async def async_get_status(self) -> BrioWilStatus:
        """Query the device and return its parsed status."""
        raw = await self._async_send("")
        text = raw.decode("ascii", errors="replace")
        _LOGGER.debug("BRiO WiL raw status from %s: %r", self._host, text)
        return _parse_status(text)

    async def async_set_mode(self, mode: int) -> None:
        """Set the light color/pattern mode."""
        await self._async_send(f'{{"prcn":{mode}}}')

    async def async_set_brightness(self, level: int) -> None:
        """Set the light brightness level (0-3)."""
        await self._async_send(f'{{"plum":{level}}}')

    async def async_set_speed(self, speed: int) -> None:
        """Set the pattern sequence speed (0-2)."""
        await self._async_send(f'{{"pspd":{speed}}}')

    async def async_toggle_power(self, turn_on: bool) -> None:
        """Send the power toggle command.

        The device only exposes a single toggle, so this must only be called
        when the current state actually differs from ``turn_on``.
        """
        await self._async_send('{"sprj":1}' if turn_on else '{"sprj":0}')
