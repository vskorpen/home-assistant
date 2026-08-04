"""Light platform for BRiO WiL."""

from __future__ import annotations

from typing import Any, override

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import BRIGHTNESS_LEVEL_TO_HA, MODE_NAME_TO_ID, MODES
from .coordinator import BrioWilConfigEntry, BrioWilCoordinator
from .entity import BrioWilEntity

PARALLEL_UPDATES = 1


def _brightness_ha_to_level(value: int) -> int:
    """Return the closest device brightness level (0-3) for an HA 0-255 value."""
    return min(
        BRIGHTNESS_LEVEL_TO_HA, key=lambda level: abs(BRIGHTNESS_LEVEL_TO_HA[level] - value)
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BrioWilConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the BRiO WiL light from a config entry."""
    async_add_entities([BrioWilLight(entry.runtime_data)])


class BrioWilLight(BrioWilEntity, LightEntity):
    """The pool light itself: power, brightness and color/pattern mode."""

    _attr_name = None
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = list(MODES.values())

    def __init__(self, coordinator: BrioWilCoordinator) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-light"

    @property
    @override
    def is_on(self) -> bool:
        return self.coordinator.data.is_on

    @property
    @override
    def brightness(self) -> int:
        return BRIGHTNESS_LEVEL_TO_HA[self.coordinator.data.brightness]

    @property
    @override
    def effect(self) -> str | None:
        return MODES.get(self.coordinator.data.mode)

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_EFFECT in kwargs:
            await self.coordinator.client.async_set_mode(
                MODE_NAME_TO_ID[kwargs[ATTR_EFFECT]]
            )
        if ATTR_BRIGHTNESS in kwargs:
            await self.coordinator.client.async_set_brightness(
                _brightness_ha_to_level(kwargs[ATTR_BRIGHTNESS])
            )
        if not self.coordinator.data.is_on:
            await self.coordinator.client.async_toggle_power(True)
        await self.coordinator.async_request_refresh_soon()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        if self.coordinator.data.is_on:
            await self.coordinator.client.async_toggle_power(False)
        await self.coordinator.async_request_refresh_soon()
