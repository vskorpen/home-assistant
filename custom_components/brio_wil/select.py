"""Select platform for BRiO WiL (pattern sequence speed)."""

from __future__ import annotations

from typing import override

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SPEED_NAME_TO_ID, SPEEDS
from .coordinator import BrioWilConfigEntry, BrioWilCoordinator
from .entity import BrioWilEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BrioWilConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the BRiO WiL speed select from a config entry."""
    async_add_entities([BrioWilSpeedSelect(entry.runtime_data)])


class BrioWilSpeedSelect(BrioWilEntity, SelectEntity):
    """Pattern sequence speed; only meaningful for animated modes."""

    _attr_translation_key = "sequence_speed"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(SPEEDS.values())

    def __init__(self, coordinator: BrioWilCoordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-speed"

    @property
    @override
    def current_option(self) -> str | None:
        return SPEEDS.get(self.coordinator.data.speed)

    @override
    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.async_set_speed(SPEED_NAME_TO_ID[option])
        await self.coordinator.async_request_refresh_soon()
