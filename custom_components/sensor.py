"""Support for Poolsync sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from time import time
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import UTC

from .const import DOMAIN
from .entity import PoolsyncDataUpdateCoordinator, PoolsyncEntity


@dataclass
class RequiredKeysMixin:
    """Required keys mixin."""

    value_fn: Callable[[dict], Any]


@dataclass
class PoolsyncSensorEntityDescription(SensorEntityDescription, RequiredKeysMixin):
    """Poolsync sensor entity description."""


def convert_timestamp(_ts: float) -> datetime:
    """Convert a timestamp to a datetime."""
    return datetime.fromtimestamp(_ts / (1000 if _ts > time() else 1), UTC)


SENSOR_MAP: dict[str | None, tuple[PoolsyncSensorEntityDescription, ...]] = {
    None: (),
    "chlorSync": (
        PoolsyncSensorEntityDescription(
            key="salt_level",
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="salt_level",
            value_fn=lambda device: device.saltLevel,
        ),
        PoolsyncSensorEntityDescription(
            key="water_temp",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            translation_key="water_temp",
            value_fn=lambda device: device.waterTemp,
        ),
        PoolsyncSensorEntityDescription(
            key="flow_rate",
            # device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            # native_unit_of_measurement=UnitOfVolumeFlowRate.GALLONS_PER_MINUTE,
            state_class=SensorStateClass.MEASUREMENT,
            translation_key="flow_rate",
            icon="mdi:water-sync",
            value_fn=lambda device: device.flowRate,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Poolsync sensors using config entry."""
    coordinator: PoolsyncDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        PoolsyncSensorEntity(
            coordinator=coordinator,
            config_entry=config_entry,
            description=description,
            device_id=device.hubId + "-" + str(device.deviceIndex),
        )
        for device in coordinator.get_devices()
        for device_type, descriptions in SENSOR_MAP.items()
        for description in descriptions
        if device_type is None or device.deviceType == device_type
    ]

    if not entities:
        return

    async_add_entities(entities)


class PoolsyncSensorEntity(PoolsyncEntity, SensorEntity):
    """Poolsync sensor entity."""

    entity_description: PoolsyncSensorEntityDescription

    @property
    def native_value(self) -> str | int | datetime | None:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self.get_device())
