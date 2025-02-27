"""Poolsync entities."""
from __future__ import annotations

from typing import Any

from pypoolsync import PoolsyncDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MAKER
from .coordinator import PoolsyncDataUpdateCoordinator


class PoolsyncEntity(CoordinatorEntity[PoolsyncDataUpdateCoordinator]):
    """Base class for Poolsync entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PoolsyncDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: EntityDescription,
        device_id: str,
    ) -> None:
        """Construct a PoolsyncEntity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self.entity_description = description
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}-{description.key}"

        device = self.get_device()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=MAKER,
            model=device.device_name,
            name=device.device_name,
        )

    def get_device(self) -> PoolsyncDevice | None:
        """Get the device from the coordinator."""
        return self.coordinator.get_device(self._device_id)
