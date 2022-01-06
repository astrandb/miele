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
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
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


@dataclass
class MieleClimateDefinition:
    """Class for defining switch entities."""

    types: tuple[int, ...]
    description: MieleClimateDescription = None


CLIMATE_TYPES: Final[tuple[MieleClimateDefinition, ...]] = (
    MieleClimateDefinition(
        types=[19, 20, 21, 32, 33, 34, 68],
        description=MieleClimateDescription(
            key="thermostat",
            currentTemperature_tag="state|temperature|0|value_raw",
            targetTemperature_tag="state|targetTemperature|0|value_raw",
            type_key="ident|type|value_localized",
            name="Zone 1",
            temperature_unit=TEMP_CELSIUS,
            precision=1.0,
            target_temperature_step=1.0,
            hvac_modes=[HVAC_MODE_COOL],
            supported_features=SUPPORT_TARGET_TEMPERATURE,
        ),
    ),
    MieleClimateDefinition(
        types=[19, 20, 21, 32, 33, 34, 68],
        description=MieleClimateDescription(
            key="thermostat_z2",
            currentTemperature_tag="state|temperature|1|value_raw",
            targetTemperature_tag="state|targetTemperature|1|value_raw",
            type_key="ident|type|value_localized",
            name="Zone 2",
            temperature_unit=TEMP_CELSIUS,
            precision=1.0,
            target_temperature_step=1.0,
            hvac_modes=[HVAC_MODE_COOL],
            supported_features=SUPPORT_TARGET_TEMPERATURE,
        ),
    ),
    MieleClimateDefinition(
        types=[19, 20, 21, 32, 33, 34, 68],
        description=MieleClimateDescription(
            key="thermostat_z3",
            currentTemperature_tag="state|temperature|2|value_raw",
            targetTemperature_tag="state|targetTemperature|2|value_raw",
            type_key="ident|type|value_localized",
            name="Zone 3",
            temperature_unit=TEMP_CELSIUS,
            precision=1.0,
            target_temperature_step=1.0,
            hvac_modes=[HVAC_MODE_COOL],
            supported_features=SUPPORT_TARGET_TEMPERATURE,
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

    def _skip_temp_zone(key: str):
        if (
            key == "thermostat_z2"
            and coordinator.data[ent].get("state|temperature|1|value_raw", -32768)
            == -32768
        ):
            return True
        if (
            key == "thermostat_z3"
            and coordinator.data[ent].get("state|temperature|2|value_raw", -32768)
            == -32768
        ):
            return True
        return False

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in CLIMATE_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                if _skip_temp_zone(definition.description.key):
                    continue
                entities.append(
                    MieleClimate(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Sensor."""

    entity_description: MieleClimateDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleClimateDescription,
        hass,
        entry,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id]["api"]

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

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        _LOGGER.debug("kwargs: %s", kwargs)
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._api.set_target_temperature(self._ent, temperature)
        await self.coordinator.async_request_refresh()

    @property
    def available(self):
        """Return the availability of the entity."""
        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255
