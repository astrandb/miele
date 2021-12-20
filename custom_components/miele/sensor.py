"""Platform for Miele sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    DEVICE_CLASS_TEMPERATURE,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)
from homeassistant.const import TEMP_CELSIUS
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
        MieleSensor(coordinator, idx, ent) for idx, ent in enumerate(coordinator.data)
    )


class MieleSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, ent):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self._state = None
        _LOGGER.debug("init sensor %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent]['ident|type|value_localized']} Temperature"
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        self._attr_native_unit_of_measurement = TEMP_CELSIUS
        self._attr_state_class = STATE_CLASS_MEASUREMENT
        self._attr_unique_id = f"temp-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent]["ident|type|value_localized"],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"
            ],
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return round(
            self.coordinator.data[self._ent]["state|temperature|0|value_raw"]
            / 100,
            1,
        )
