"""DataUpdateCoordinator for the BRiO WiL integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import override

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BrioWilClient, BrioWilError, BrioWilStatus
from .const import COMMAND_REFRESH_DELAY, DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)

type BrioWilConfigEntry = ConfigEntry[BrioWilCoordinator]


class BrioWilCoordinator(DataUpdateCoordinator[BrioWilStatus]):
    """Poll a BRiO WiL device for its current status."""

    config_entry: BrioWilConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: BrioWilConfigEntry, client: BrioWilClient
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.client = client

    @override
    async def _async_update_data(self) -> BrioWilStatus:
        try:
            return await self.client.async_get_status()
        except BrioWilError as err:
            raise UpdateFailed(str(err)) from err

    async def async_request_refresh_soon(self) -> None:
        """Refresh shortly after a write command, once the device applies it.

        The device only reflects a command in its status telegram after a
        short delay; polling immediately would just re-read the stale state.
        """
        await asyncio.sleep(COMMAND_REFRESH_DELAY)
        await self.async_request_refresh()
