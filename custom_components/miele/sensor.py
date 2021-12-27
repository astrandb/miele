"""Platform for Miele sensor integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import TEMP_CELSIUS
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

STATE_STATUS = {
    0: "Reserved",
    1: "Off",
    2: "On",
    3: "Programmed",
    4: "Programmed Waiting to start",
    5: "Running",
    6: "Pause",
    7: "End Programmed",
    8: "Failure",
    9: "Programme interrupted",
    10: "Idle",
    11: "Rinse hold",
    13: "Superfreezing",
    14: "Supercooling",
    15: "Superheating",
    146: "Suppercooling/Superfreezing",
    255: "Not connected",
}


@dataclass
class MieleSensorDescription(SensorEntityDescription):
    """Class describing Weatherlink sensor entities."""

    data_tag: str | None = None
    type_key: str | None = None
    convert: Callable[[Any], Any] | None = None
    decimals: int = 1


@dataclass
class MieleSensorDefinition:
    """Class for defining sensor entities."""

    types: tuple[int, ...]
    description: MieleSensorDescription = None


SENSOR_TYPES: Final[tuple[MieleSensorDefinition, ...]] = (
    MieleSensorDefinition(
        types=[12, 13, 15, 16, 19, 20, 21, 31, 32, 33, 34, 45, 67, 68],
        description=MieleSensorDescription(
            key="temperature",
            data_tag="state|temperature|0|value_raw",
            type_key="ident|type|value_localized",
            device_class=SensorDeviceClass.TEMPERATURE,
            name="Temperature",
            native_unit_of_measurement=TEMP_CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x: x / 100.0,
        ),
    ),
    MieleSensorDefinition(
        types=[12, 13, 15, 16, 19, 20, 21, 31, 32, 33, 34, 45, 67, 68],
        description=MieleSensorDescription(
            key="targetTemperature",
            data_tag="state|targetTemperature|0|value_raw",
            type_key="ident|type|value_localized",
            device_class=SensorDeviceClass.TEMPERATURE,
            name="Target Temperature",
            native_unit_of_measurement=TEMP_CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x: x / 100.0,
        ),
    ),
    MieleSensorDefinition(
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
        description=MieleSensorDescription(
            key="stateStatus",
            data_tag="state|status|value_raw",
            type_key="ident|type|value_localized",
            name="Status",
            icon="mdi:state-machine",
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x: STATE_STATUS.get(x, x),
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
        for definition in SENSOR_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleSensor(coordinator, idx, ent, definition.description)
                )

    async_add_entities(entities)


class MieleSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    entity_description: MieleSensorDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleSensorDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init sensor %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent][self.entity_description.type_key]} {self.entity_description.name}"
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent][self.entity_description.type_key],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.convert is None:
            return self.coordinator.data[self._ent][self.entity_description.data_tag]
        else:
            return self.entity_description.convert(
                self.coordinator.data[self._ent][self.entity_description.data_tag]
            )
