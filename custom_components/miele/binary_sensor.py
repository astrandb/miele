"""Platform for Miele binary_sensor integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleBinarySensorDescription(BinarySensorEntityDescription):
    """Class describing Miele binary sensor entities."""

    data_tag: str | None = None
    type_key: str | None = None
    convert: Callable[[Any], Any] | None = None


BINARY_SENSOR_TYPES: Final[tuple[MieleBinarySensorDescription, ...]] = (
    MieleBinarySensorDescription(
        key="door",
        data_tag="state|signalDoor",
        type_key="ident|type|value_localized",
        device_class=BinarySensorDeviceClass.DOOR,
        name="Door",
    ),
    MieleBinarySensorDescription(
        key="info",
        data_tag="state|signalInfo",
        type_key="ident|type|value_localized",
        device_class=BinarySensorDeviceClass.PROBLEM,
        name="Info",
    ),
    MieleBinarySensorDescription(
        key="failure",
        data_tag="state|signalFailure",
        type_key="ident|type|value_localized",
        device_class=BinarySensorDeviceClass.PROBLEM,
        name="Failure",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = await get_coordinator(hass, config_entry)

    async_add_entities(
        MieleBinarySensor(coordinator, idx, ent, description)
        for idx, ent in enumerate(coordinator.data)
        for description in BINARY_SENSOR_TYPES
    )


class MieleBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Binary Sensor."""

    entity_description: MieleBinarySensorDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleBinarySensorDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init sensor %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent]['ident|type|value_localized']} {self.entity_description.name}"
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent][self.entity_description.type_key],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._ent][self.entity_description.data_tag]
