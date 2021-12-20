"""Platform for Miele binary_sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_DOOR,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = await get_coordinator(hass, config_entry)

    async_add_entities(
        MieleBinarySensor(coordinator, idx, ent) for idx, ent in enumerate(coordinator.data)
    )


class MieleBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Binary Sensor."""

    def __init__(self, coordinator, idx, ent):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self._state = None
        _LOGGER.debug("init sensor %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent]['ident|type|value_localized']} Door"
        self._attr_device_class = DEVICE_CLASS_DOOR
        self._attr_unique_id = f"door-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent]["ident|type|value_localized"],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"
            ],
        )

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._ent]["state|signalDoor"]
