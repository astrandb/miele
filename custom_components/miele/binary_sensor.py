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
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
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


@dataclass
class MieleBinarySensorDefinition:
    """Class for defining binary sensor entities."""

    types: tuple[int, ...]
    description: MieleBinarySensorDescription = None


BINARY_SENSOR_TYPES: Final[tuple[MieleBinarySensorDefinition, ...]] = (
    MieleBinarySensorDefinition(
        types=[12, 13, 15, 16, 19, 20, 21, 31, 32, 33, 34, 45, 67],
        description=MieleBinarySensorDescription(
            key="door",
            data_tag="state|signalDoor",
            type_key="ident|type|value_localized",
            device_class=BinarySensorDeviceClass.DOOR,
            name="Door",
        ),
    ),
    MieleBinarySensorDefinition(
        types=[
            1,
            2,
            7,
            12,
            13,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            23,
            24,
            25,
            31,
            32,
            33,
            34,
            45,
            67,
            68,
        ],
        description=MieleBinarySensorDescription(
            key="info",
            data_tag="state|signalInfo",
            type_key="ident|type|value_localized",
            device_class=BinarySensorDeviceClass.PROBLEM,
            name="Info",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleBinarySensorDefinition(
        types=[
            1,
            2,
            7,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            23,
            24,
            25,
            27,
            31,
            32,
            33,
            34,
            45,
            67,
            68,
        ],
        description=MieleBinarySensorDescription(
            key="failure",
            data_tag="state|signalFailure",
            type_key="ident|type|value_localized",
            device_class=BinarySensorDeviceClass.PROBLEM,
            name="Failure",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in BINARY_SENSOR_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleBinarySensor(coordinator, idx, ent, definition.description)
                )

    async_add_entities(entities)


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

    @property
    def available(self):
        """Return the availability of the entity."""
        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255
