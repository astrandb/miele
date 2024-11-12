"""Platform for Miele integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, Final

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
)
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import get_coordinator
from .const import (
    ACTIONS,
    API,
    DOMAIN,
    TARGET_TEMPERATURE,
    MieleAppliance,
)
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleClimateDescription(ClimateEntityDescription):
    """Class describing Miele climate entities."""

    current_temperature_tag: str | None = None
    target_temperature_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    convert: Callable[[Any], Any] | None = None
    temperature_unit: str = None
    precision: float | None = None
    max_temp: float | None = None
    min_temp: float | None = None
    target_temperature_step: float | None = None
    hvac_modes: list | None = None
    zone: int = 0
    supported_features: ClimateEntityFeature = ClimateEntityFeature(0)


@dataclass
class MieleClimateDefinition:
    """Class for defining climate entities."""

    types: tuple[MieleAppliance, ...]
    description: MieleClimateDescription = None


CLIMATE_TYPES: Final[tuple[MieleClimateDefinition, ...]] = (
    MieleClimateDefinition(
        types=[
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.WINE_CABINET_FREEZER,
        ],
        description=MieleClimateDescription(
            key="thermostat",
            current_temperature_tag="state|temperature|0|value_raw",
            target_temperature_tag="state|targetTemperature|0|value_raw",
            name="Zone 1",
            temperature_unit=UnitOfTemperature.CELSIUS,
            precision=1.0,
            target_temperature_step=1.0,
            hvac_modes=[HVACMode.COOL],
            zone=0,
            supported_features=ClimateEntityFeature.TARGET_TEMPERATURE,
        ),
    ),
    MieleClimateDefinition(
        types=[
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.WINE_CABINET_FREEZER,
        ],
        description=MieleClimateDescription(
            key="thermostat",
            current_temperature_tag="state|temperature|1|value_raw",
            target_temperature_tag="state|targetTemperature|1|value_raw",
            name="Zone 2",
            temperature_unit=UnitOfTemperature.CELSIUS,
            precision=1.0,
            target_temperature_step=1.0,
            hvac_modes=[HVACMode.COOL],
            zone=1,
            supported_features=ClimateEntityFeature.TARGET_TEMPERATURE,
        ),
    ),
    MieleClimateDefinition(
        types=[
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.WINE_CABINET_FREEZER,
        ],
        description=MieleClimateDescription(
            key="thermostat",
            current_temperature_tag="state|temperature|2|value_raw",
            target_temperature_tag="state|targetTemperature|2|value_raw",
            name="Zone 3",
            temperature_unit=UnitOfTemperature.CELSIUS,
            precision=1.0,
            target_temperature_step=1.0,
            hvac_modes=[HVACMode.COOL],
            zone=2,
            supported_features=ClimateEntityFeature.TARGET_TEMPERATURE,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = [
        MieleClimate(coordinator, idx, ent, definition.description, hass, config_entry)
        for idx, ent in enumerate(coordinator.data)
        for definition in CLIMATE_TYPES
        if coordinator.data[ent]["ident|type|value_raw"] in definition.types
        and coordinator.data[ent].get(
            definition.description.target_temperature_tag, -32768
        )
        != -32768
    ]

    async_add_entities(entities)


class MieleClimate(MieleEntity, ClimateEntity):
    """Representation of a climate entity."""

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
        """Initialize the climate entity."""
        super().__init__(coordinator, idx, ent, description)
        self._eid = hass.data[DOMAIN][entry.entry_id]
        self._api = self._eid[API]

        self._ed = description
        _LOGGER.debug("init climate %s", ent)
        # _LOGGER.debug(
        #   "Type: %s, Zone: %s",
        #   self.coordinator.data[self._ent]["ident|type|value_raw"], self._ed.zone,
        # )

        if (
            self.coordinator.data[self._ent]["ident|type|value_raw"] == 21
            and self._ed.zone == 0
        ):
            name = "fridge"
        elif (
            self.coordinator.data[self._ent]["ident|type|value_raw"] == 21
            and self._ed.zone == 1
        ):
            name = "freezer"
        elif (
            self.coordinator.data[self._ent]["ident|type|value_raw"] == 19
            and self._ed.zone == 0
        ):
            name = "fridge"
        elif (
            self.coordinator.data[self._ent]["ident|type|value_raw"] == 20
            and self._ed.zone == 0
        ):
            name = "freezer"
        else:
            name = self._ed.name
        self._attr_translation_key = name

        zone = "" if self._ed.zone == 0 else f"{self._ed.zone}-"
        # deviates from MieleEntity
        self._attr_unique_id = f"{self._ed.key}-{zone}{self._ent}"
        self._attr_temperature_unit = self._ed.temperature_unit
        self._attr_precision = self._ed.precision
        try:
            self._attr_max_temp = self._eid[ACTIONS][self._ent][TARGET_TEMPERATURE][
                self._ed.zone
            ]["max"]
        except (IndexError, KeyError):
            _LOGGER.debug("Could not retreive max_target_temp on %s from API", name)
            self._attr_max_temp = None
        try:
            self._attr_min_temp = self._eid[ACTIONS][self._ent][TARGET_TEMPERATURE][
                self._ed.zone
            ]["min"]
        except (IndexError, KeyError):
            _LOGGER.debug("Could not retreive min_target_temp %s from API", name)
            self._attr_min_temp = None

        self._attr_target_temperature_step = self._ed.target_temperature_step
        self._attr_hvac_modes = self._ed.hvac_modes
        self._attr_hvac_mode = HVACMode.COOL
        self._attr_supported_features = self._ed.supported_features

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return round(
            self.coordinator.data[self._ent][self._ed.current_temperature_tag] / 100,
            1,
        )

    @property
    def target_temperature(self):
        """Return the target temperature."""
        if self.coordinator.data[self._ent].get(
            self._ed.target_temperature_tag, -32768
        ) in (
            -32766,
            -32768,
        ):
            return None
        return round(
            self.coordinator.data[self._ent][self._ed.target_temperature_tag] / 100,
            1,
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        _LOGGER.debug("kwargs: %s", kwargs)
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._api.set_target_temperature(
            self._ent, temperature, self._ed.zone + 1
        )
        await self.coordinator.async_request_refresh()

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255
