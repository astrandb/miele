"""Platform for Miele sensor integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Final

from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription
from homeassistant.components.climate.const import (
    HVAC_MODE_COOL,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import TEMP_CELSIUS
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
from .devcap import LIVE_ACTION_CAPABILITIES

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleClimateDescription(ClimateEntityDescription):
    """Class describing Weatherlink sensor entities."""

    currentTemperature_tag: str | None = None
    targetTemperature_tag: str | None = None
    type_key: str | None = None
    convert: Callable[[Any], Any] | None = None
    decimals: int = 1
    temperature_unit: str = None
    precision: float | None = None
    max_temp: float | None = None
    min_temp: float | None = None
    target_temperature_step: float | None = None
    hvac_modes: list | None = None
    supported_features: int = 0


CLIMATE_TYPES: Final[tuple[MieleClimateDescription, ...]] = (
    MieleClimateDescription(
        key="thermostat",
        currentTemperature_tag="state|temperature|0|value_raw",
        targetTemperature_tag="state|targetTemperature|0|value_raw",
        type_key="ident|type|value_localized",
        name="Zone 1",
        temperature_unit=TEMP_CELSIUS,
        precision=1.0,
        # max_temp=8.0,
        # min_temp=-26.0,
        target_temperature_step=1.0,
        hvac_modes=[HVAC_MODE_COOL],
        supported_features=SUPPORT_TARGET_TEMPERATURE,
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
        MieleClimate(coordinator, idx, ent, description)
        for idx, ent in enumerate(coordinator.data)
        for description in CLIMATE_TYPES
    )


class MieleClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Sensor."""

    entity_description: MieleClimateDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleClimateDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init sensor %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent][self.entity_description.type_key]} {self.entity_description.name}"
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_temperature_unit = self.entity_description.temperature_unit
        self._attr_precision = self.entity_description.precision
        self._attr_max_temp = LIVE_ACTION_CAPABILITIES[self._ent]["targetTemperature"][
            0
        ]["max"]
        self._attr_min_temp = LIVE_ACTION_CAPABILITIES[self._ent]["targetTemperature"][
            0
        ]["min"]
        self._attr_target_temperature_step = (
            self.entity_description.target_temperature_step
        )
        self._attr_hvac_modes = self.entity_description.hvac_modes
        self._attr_hvac_mode = HVAC_MODE_COOL
        self._attr_supported_features = self.entity_description.supported_features
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent][self.entity_description.type_key],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def current_temperature(self):
        """Return the state of the sensor."""
        return round(
            self.coordinator.data[self._ent][
                self.entity_description.currentTemperature_tag
            ]
            / 100,
            1,
        )

    @property
    def target_temperature(self):
        """Return the state of the sensor."""
        return round(
            self.coordinator.data[self._ent][
                self.entity_description.targetTemperature_tag
            ]
            / 100,
            1,
        )

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
