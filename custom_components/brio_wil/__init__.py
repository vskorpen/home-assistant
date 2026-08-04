"""The BRiO WiL integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .api import BrioWilClient
from .coordinator import BrioWilConfigEntry, BrioWilCoordinator

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: BrioWilConfigEntry) -> bool:
    """Set up BRiO WiL from a config entry."""
    client = BrioWilClient(entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = BrioWilCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BrioWilConfigEntry) -> bool:
    """Unload a BRiO WiL config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
