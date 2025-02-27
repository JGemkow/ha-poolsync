"""Number platform for Poolsync Chlorsync SWGs."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from pypoolsync import PoolSyncChlorsyncSWG

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PoolsyncDataUpdateCoordinator
from .entity import PoolsyncEntity


@dataclass(frozen=True, kw_only=True)
class PoolsyncNumberEntityDescription(
    NumberEntityDescription,
):
    """Description of a Poolsync number entity."""

    value: Callable[[PoolSyncChlorsyncSWG, int], float | None]
    number_option_fn: Callable[
        [PoolsyncDataUpdateCoordinator, str], Coroutine[Any, Any, bool]
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator: PoolsyncDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        PoolsyncNumberEntity(
            coordinator=coordinator,
            config_entry=config_entry,
            description=PoolsyncNumberEntityDescription(
                key="chlor_output",
                icon="mdi:waves-arrow-up",
                translation_key="chlor_output",
                native_step=1.0,
                value=lambda device: device.chlor_output,
                number_option_fn=lambda coordinator,
                option,
                device: coordinator.change_chlor_output(device, int(option)),
            ),
            device_id=device.hub_id + "-" + str(device.device_index),
        )
        for device in coordinator.get_devices()
        if device.device_type in ["chlorSync"]
    ]

    if not entities:
        return

    async_add_entities(entities)


class PoolsyncNumberEntity(PoolsyncEntity, NumberEntity):
    """Poolsync number entity."""

    entity_description: PoolsyncNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        """State of the number entity."""
        return self.entity_description.value(self.get_device())

    async def async_set_native_value(self, value: float) -> None:
        """Change the number option."""
        await self.entity_description.number_option_fn(
            self.coordinator, value, self.get_device()
        )
        self.async_write_ha_state()
