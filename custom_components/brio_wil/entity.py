"""Shared base entity for BRiO WiL."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BrioWilCoordinator


class BrioWilEntity(CoordinatorEntity[BrioWilCoordinator]):
    """Base entity tying every BRiO WiL entity to the same device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BrioWilCoordinator) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
